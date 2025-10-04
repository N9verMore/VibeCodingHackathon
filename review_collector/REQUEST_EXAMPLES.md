# Request Examples for Review Collector Lambda

## Unified Request Schema

All requests follow the same structure regardless of invocation method.

### Required Fields

```json
{
  "source": "appstore | googleplay | trustpilot",
  "app_identifier": "platform-specific identifier",
  "brand": "brand/company name"
}
```

### Optional Fields

```json
{
  "limit": 100,           // Max reviews to collect (1-500, default: 100)
  "country": "us",        // Country code (default: "us")
  "metadata": {}          // Optional metadata for tracking
}
```

---

## Platform-Specific Identifiers

### App Store
- **Identifier**: Numeric App ID
- **Example**: `"544007664"` (Telegram)
- **How to find**: URL like `https://apps.apple.com/us/app/telegram-messenger/id544007664`

### Google Play
- **Identifier**: Package name
- **Example**: `"org.telegram.messenger"` (Telegram)
- **How to find**: URL like `https://play.google.com/store/apps/details?id=org.telegram.messenger`

### Trustpilot
- **Identifier**: Domain name
- **Example**: `"telegram.org"` (Telegram)
- **How to find**: Trustpilot URL like `https://www.trustpilot.com/review/telegram.org`

---

## Method 1: API Gateway (HTTP POST)

### cURL Example - App Store

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100,
    "country": "us"
  }'
```

### cURL Example - Google Play

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "googleplay",
    "app_identifier": "org.telegram.messenger",
    "brand": "telegram",
    "limit": 50
  }'
```

### cURL Example - Trustpilot

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "telegram.org",
    "brand": "telegram",
    "limit": 20
  }'
```

### JavaScript/Fetch Example

```javascript
const response = await fetch('https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    source: 'appstore',
    app_identifier: '544007664',
    brand: 'telegram',
    limit: 100,
    country: 'us'
  })
});

const data = await response.json();
console.log(data);
```

### Python Requests Example

```python
import requests

response = requests.post(
    'https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews',
    json={
        'source': 'googleplay',
        'app_identifier': 'org.telegram.messenger',
        'brand': 'telegram',
        'limit': 100
    }
)

print(response.json())
```

---

## Method 2: Direct Lambda Invoke

### AWS CLI - App Store

```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100
  }' \
  --profile hackathon \
  response.json
```

### AWS CLI - Google Play

```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "googleplay",
    "app_identifier": "org.telegram.messenger",
    "brand": "telegram",
    "limit": 50
  }' \
  --profile hackathon \
  response.json
```

### Python Boto3 Example

```python
import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

response = lambda_client.invoke(
    FunctionName='serpapi-collector-lambda',
    InvocationType='RequestResponse',
    Payload=json.dumps({
        'source': 'appstore',
        'app_identifier': '544007664',
        'brand': 'telegram',
        'limit': 100,
        'country': 'us'
    })
)

result = json.loads(response['Payload'].read())
print(result)
```

---

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Reviews collected successfully",
  "statistics": {
    "brand": "telegram",
    "app_identifier": "544007664",
    "fetched": 100,
    "saved": 95,
    "skipped": 5,
    "errors": 0,
    "duration_seconds": 12.5,
    "start_time": "2024-10-04T14:30:00.000000",
    "end_time": "2024-10-04T14:30:12.500000"
  },
  "request": {
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100,
    "country": "us",
    "metadata": {}
  }
}
```

### Error Response - Validation Error

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid source: 'invalid_source'. Must be one of: appstore, googleplay, trustpilot",
  "request": {
    "source": "invalid_source",
    "app_identifier": "544007664",
    "brand": "telegram"
  }
}
```

### Error Response - Missing Field

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "'app_identifier' must be a non-empty string",
  "request": {
    "source": "appstore",
    "brand": "telegram"
  }
}
```

### Error Response - Internal Error

```json
{
  "success": false,
  "error": "InternalServerError",
  "message": "Failed to connect to SerpAPI",
  "request": {
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100
  }
}
```

---

## Validation Rules

### Source
- **Type**: string
- **Required**: Yes
- **Valid values**: `appstore`, `googleplay`, `trustpilot` (case-insensitive)

### App Identifier
- **Type**: string
- **Required**: Yes
- **Format**: Platform-specific (see above)

### Brand
- **Type**: string
- **Required**: Yes
- **Format**: Any non-empty string

### Limit
- **Type**: integer
- **Required**: No (default: 100)
- **Range**: 1 to 500

### Country
- **Type**: string
- **Required**: No (default: "us")
- **Format**: 2-letter country code (ISO 3166-1 alpha-2)

### Metadata
- **Type**: object
- **Required**: No (default: {})
- **Format**: Any valid JSON object

---

## Common Use Cases

### Collect Latest Reviews

```json
{
  "source": "appstore",
  "app_identifier": "544007664",
  "brand": "telegram",
  "limit": 100
}
```
> Collects 100 most recent reviews from App Store (US)

### Collect from Specific Country

```json
{
  "source": "appstore",
  "app_identifier": "544007664",
  "brand": "telegram",
  "limit": 50,
  "country": "gb"
}
```
> Collects 50 most recent reviews from App Store (UK)

### Collect with Tracking Metadata

```json
{
  "source": "googleplay",
  "app_identifier": "org.telegram.messenger",
  "brand": "telegram",
  "limit": 100,
  "metadata": {
    "campaign_id": "campaign_001",
    "collected_by": "automated_daily_job",
    "notes": "Daily review collection"
  }
}
```
> Collects reviews with additional tracking information

---

## Tips & Best Practices

1. **Limit Usage**:
   - App Store: ~25 reviews per page, recommend limit ≤ 200
   - Google Play: ~20 reviews per page, recommend limit ≤ 200
   - Trustpilot: Max 20 reviews (single page)

2. **Rate Limiting**:
   - SerpAPI has rate limits based on your plan
   - Consider spacing out requests for large volumes

3. **Country Codes**:
   - Use lowercase 2-letter codes: `us`, `gb`, `de`, `fr`, etc.
   - App Store respects country parameter
   - Google Play may have limited country support

4. **Error Handling**:
   - Always check the `success` field in response
   - Handle `ValidationError` (400) and `InternalServerError` (500)
   - Implement retry logic for transient errors

5. **Idempotency**:
   - Lambda automatically deduplicates reviews based on `content_hash`
   - Safe to re-run the same request multiple times
   - Only new or updated reviews will be saved

