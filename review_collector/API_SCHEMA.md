# Review Collector API Schema

## Quick Reference

### Endpoint
```
POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews
```

### Minimal Request
```json
{
  "source": "appstore",
  "app_identifier": "544007664",
  "brand": "telegram"
}
```

### Full Request Schema
```json
{
  "source": "appstore | googleplay | trustpilot",  // Required
  "app_identifier": "string",                      // Required, platform-specific
  "brand": "string",                               // Required
  "limit": 100,                                    // Optional, 1-500, default: 100
  "country": "us",                                 // Optional, ISO 3166-1 alpha-2
  "metadata": {}                                   // Optional, any JSON object
}
```

---

## Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source` | string | ✅ Yes | - | Platform: `appstore`, `googleplay`, or `trustpilot` |
| `app_identifier` | string | ✅ Yes | - | Platform-specific identifier (see below) |
| `brand` | string | ✅ Yes | - | Brand/company name for filtering |
| `limit` | integer | ❌ No | 100 | Max reviews to collect (1-500) |
| `country` | string | ❌ No | `us` | 2-letter country code |
| `metadata` | object | ❌ No | `{}` | Custom metadata for tracking |

---

## App Identifiers by Platform

### App Store
- **Format**: Numeric ID
- **Example**: `"544007664"`
- **Find it**: In URL `https://apps.apple.com/.../id544007664`

### Google Play  
- **Format**: Package name
- **Example**: `"org.telegram.messenger"`
- **Find it**: In URL `https://play.google.com/store/apps/details?id=org.telegram.messenger`

### Trustpilot
- **Format**: Domain name
- **Example**: `"telegram.org"`
- **Find it**: In URL `https://www.trustpilot.com/review/telegram.org`

---

## Response Format

### ✅ Success (200)
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
    "start_time": "2024-10-04T14:30:00",
    "end_time": "2024-10-04T14:30:12.5"
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

### ❌ Validation Error (400)
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid source: 'xxx'. Must be one of: appstore, googleplay, trustpilot",
  "request": {...}
}
```

### ❌ Server Error (500)
```json
{
  "success": false,
  "error": "InternalServerError",
  "message": "Error details...",
  "request": {...}
}
```

---

## Quick Examples

### cURL
```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{"source":"appstore","app_identifier":"544007664","brand":"telegram","limit":100}'
```

### Python
```python
import requests

response = requests.post(
    'https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews',
    json={
        'source': 'googleplay',
        'app_identifier': 'org.telegram.messenger',
        'brand': 'telegram',
        'limit': 50
    }
)
print(response.json())
```

### JavaScript
```javascript
const response = await fetch('https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    source: 'trustpilot',
    app_identifier: 'telegram.org',
    brand: 'telegram',
    limit: 20
  })
});
const data = await response.json();
```

---

## Features

✅ **Unified Schema** - Same request format for all platforms  
✅ **Automatic Validation** - Input validation with clear error messages  
✅ **Idempotent** - Safe to retry, no duplicates  
✅ **Sorted** - Returns newest reviews first  
✅ **Paginated** - Automatically handles pagination  
✅ **Deduplicated** - Content-based deduplication via hash  

---

## Limits & Constraints

| Platform | Reviews per Page | Recommended Max Limit | Notes |
|----------|------------------|----------------------|-------|
| App Store | ~25 | 200 | Sorted by most recent |
| Google Play | ~20 | 200 | Sorted by newest (`sort_by=2`) |
| Trustpilot | 20 (max) | 20 | Single page only |

---

## Error Codes

| Status | Error | Description |
|--------|-------|-------------|
| 200 | - | Success |
| 400 | ValidationError | Invalid request parameters |
| 500 | InternalServerError | Server-side error |

---

For more detailed examples, see [REQUEST_EXAMPLES.md](REQUEST_EXAMPLES.md)

