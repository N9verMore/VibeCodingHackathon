##  Reddit Collector - Deployment Guide

Гайд по deployment Reddit collector Lambda та інтеграції в систему.

---

## 📋 Що було створено

### 1. Lambda Function - `reddit-collector-lambda`
- **Код:** `src/reddit_collector/`
  - `handler.py` - Main Lambda handler
  - `reddit_client.py` - Reddit API client (PRAW)
  - `reddit_mapper.py` - Mapping Reddit posts → Review entities
  - `request_schema.py` - Request/response schemas
  - `requirements.txt` - Dependencies (praw, langdetect)

### 2. Domain Model Updates
- ✅ Додано `ReviewSource.REDDIT` до enum
- ✅ Оновлено валідацію rating: дозволено `-1` (для Reddit постів без рейтингу)
- ✅ Додано `get_reddit_credentials()` до `SecretsClient`

### 3. CDK Stack Updates
- ✅ Додано Reddit Lambda до stack
- ✅ Інтеграція в Step Functions (паралельно з іншими джерелами)
- ✅ Новий API Gateway endpoint: `/collect-reddit`

### 4. API Endpoint
```
POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/collect-reddit
```

**Request Body:**
```json
{
  "brand": "Flo",
  "keywords": "Flo app",
  "limit": 100,
  "days_back": 30,
  "sort": "new",
  "job_id": "optional_job_id"
}
```

---

## 🔐 Step 1: Add Reddit Credentials to Secrets Manager

### Ваші Reddit credentials:
- **Client ID:** `Ao_QStxK9p0cS5875yH6Ag`
- **Client Secret:** `-Y65zQvx1EBPy9rIzUX0_TYRi5Z_Yw`

### Оновіть secret в AWS Secrets Manager:

```bash
# Get current secret value
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials \
  --query SecretString \
  --output text > /tmp/current-secret.json

# Edit the file to add Reddit credentials
# Add this to the JSON:
{
  ...existing credentials...,
  "reddit": {
    "client_id": "Ao_QStxK9p0cS5875yH6Ag",
    "client_secret": "-Y65zQvx1EBPy9rIzUX0_TYRi5Z_Yw",
    "user_agent": "Brand Monitor v1.0"
  }
}

# Update the secret
aws secretsmanager update-secret \
  --secret-id review-collector/credentials \
  --secret-string file:///tmp/current-secret.json

# Clean up
rm /tmp/current-secret.json
```

**Або вручну через AWS Console:**
1. Відкрийте AWS Secrets Manager console
2. Знайдіть secret `review-collector/credentials`
3. Натисніть "Retrieve secret value" → "Edit"
4. Додайте Reddit секцію до JSON
5. Збережіть

---

## 🚀 Step 2: Deploy CDK Stack

```bash
cd /Users/myk/PycharmProjects/monitor/VibeCodingHackathon/review_collector/cdk

# Install dependencies (if needed)
pip install -r requirements.txt

# Synth to check for errors
cdk synth

# Deploy
cdk deploy
```

### Що відбудеться під час deployment:
1. ✅ Створення Reddit Lambda function
2. ✅ Packaging dependencies (praw, langdetect)
3. ✅ Додавання shared layer (domain/infrastructure code)
4. ✅ Створення `/collect-reddit` API endpoint
5. ✅ Інтеграція в Step Functions workflow
6. ✅ Налаштування permissions (DynamoDB, Secrets Manager)

---

## 🧪 Step 3: Test the API

### Test 1: Direct Lambda Invoke (Simple Test)
```bash
aws lambda invoke \
  --function-name reddit-collector-lambda \
  --payload '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 10
  }' \
  /tmp/reddit-response.json

cat /tmp/reddit-response.json | jq '.'
```

### Test 2: API Gateway (Full Test)
```bash
# Get your API URL from CDK outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name ReviewCollectorStack \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text)

echo "API URL: $API_URL"

# Test Reddit collection
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 20,
    "days_back": 30
  }' | jq '.'
```

### Test 3: Step Functions (Orchestrated)
```bash
# Start execution
aws stepfunctions start-execution \
  --state-machine-arn "arn:aws:states:REGION:ACCOUNT:stateMachine:ReviewCollectorStateMachine" \
  --input '{
    "brand": "Flo",
    "limit": 50,
    "sources": {
      "appstore": "",
      "googleplay": "",
      "trustpilot": ""
    },
    "reddit_keywords": "Flo app"
  }'
```

---

## 📊 Step 4: Verify Data in DynamoDB

```bash
# Query Reddit posts
aws dynamodb query \
  --table-name ReviewsTableV2 \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --filter-expression "#src = :source" \
  --expression-attribute-names '{"#src": "source"}' \
  --expression-attribute-values '{
    ":brand": {"S": "flo"},
    ":source": {"S": "reddit"}
  }' \
  --limit 5
```

### Expected Data Format:
```json
{
  "pk": "reddit#1nxu814",
  "id": "1nxu814",
  "source": "reddit",
  "backlink": "https://www.reddit.com/r/birthcontrol/comments/...",
  "brand": "flo",
  "app_identifier": "birthcontrol",
  "title": "Asking for peace of mind.",
  "text": "Full post text...",
  "rating": -1,
  "language": "en",
  "author_hint": "okbirdywirdy",
  "created_at": "2025-10-04T13:37:24+00:00",
  "fetched_at": "2025-10-05T02:20:05+00:00",
  "is_processed": false,
  "content_hash": "..."
}
```

---

## 🎯 Usage Examples

### Example 1: Collect Flo app mentions
```bash
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 100,
    "days_back": 30,
    "sort": "new"
  }'
```

### Example 2: Top posts about Flo Health
```bash
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo Health",
    "limit": 50,
    "days_back": 30,
    "sort": "top"
  }'
```

### Example 3: Recent posts (last 7 days)
```bash
curl -X POST "$API_URL/collect-reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 30,
    "days_back": 7,
    "sort": "new"
  }'
```

---

## 🔑 Key Features

### 1. Flexible Keyword Search
- **keywords** field дозволяє вказати точний пошуковий запит
- Приклади: "Flo app", "Flo Health", "Flo period tracker"
- Reddit шукає точну фразу (в лапках)

### 2. Rating System
- ❌ Reddit пости **НЕ мають** star rating
- ✅ Всі пости зберігаються з `rating = -1`
- 📊 Metadata зберігається: `score`, `upvote_ratio`, `num_comments`

### 3. Subreddit as app_identifier
- `app_identifier` = subreddit name
- Дозволяє групувати пости по subreddits
- Приклад: `r/birthcontrol`, `r/amipregnant`, `r/Periods`

### 4. Language Detection
- Автоматичне визначення мови через `langdetect`
- Fallback до `en` якщо detection fails

### 5. Integration with Step Functions
- Reddit збирається паралельно з App Store, Google Play, Trustpilot, News
- Використовує той же `job_id` для групування
- Error handling - якщо Reddit fails, інші джерела продовжують працювати

---

## 📝 Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `brand` | string | ✅ Yes | - | Brand name for storage |
| `keywords` | string | ✅ Yes | - | Search keywords for Reddit |
| `limit` | integer | No | 100 | Max posts to collect (1-1000) |
| `days_back` | integer | No | 30 | Days to search back (1-365) |
| `sort` | string | No | "new" | Sort order: new/hot/top/relevance |
| `job_id` | string | No | null | Job identifier for orchestration |

---

## 🔍 Response Format

### Success Response (200 OK):
```json
{
  "success": true,
  "message": "Reddit posts collected successfully",
  "statistics": {
    "fetched": 100,
    "mapped": 100,
    "saved": 98,
    "skipped": 2
  },
  "request": {
    "brand": "Flo",
    "keywords": "Flo app",
    "limit": 100,
    "days_back": 30,
    "sort": "new"
  }
}
```

### Error Response (400/500):
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "'keywords' is required",
  "request": {...}
}
```

---

## 🛠️ Troubleshooting

### Issue: "Reddit credentials not found"
**Solution:** Додайте Reddit credentials в Secrets Manager (див. Step 1)

### Issue: "PRAW not installed"
**Solution:** Lambda автоматично встановлює залежності при deployment. Redeploy:
```bash
cdk deploy --force
```

### Issue: No posts found
**Solutions:**
- Перевірте `keywords` - можливо надто специфічні
- Збільште `days_back`
- Спробуйте інший `sort` order (relevance замість new)
- Перевірте написання brand name

### Issue: Language detection fails
**Info:** Це нормально для коротких текстів. Fallback = `en`

---

## 📈 Monitoring

### CloudWatch Logs
```bash
# View logs
aws logs tail /aws/lambda/reddit-collector-lambda --follow
```

### Metrics to Watch
- **Invocations:** Кількість запитів
- **Duration:** Час виконання (очікується 5-30 sec)
- **Errors:** Помилки (повинно бути ~0%)
- **Throttles:** Rate limiting (повинно бути 0)

---

## ✅ Checklist

- [ ] Додано Reddit credentials в Secrets Manager
- [ ] Задеплоєно CDK stack
- [ ] Протестовано `/collect-reddit` endpoint
- [ ] Перевірено дані в DynamoDB
- [ ] Протестовано інтеграцію в Step Functions
- [ ] Налаштовано CloudWatch Alarms (optional)

---

## 🚀 Next Steps

1. ✅ Deployment успішний
2. 📊 Зібрати першу партію даних
3. 📈 Налаштувати регулярний збір (EventBridge)
4. 🔍 Інтегрувати в аналітику/дашборди
5. 🎯 Налаштувати алерти для важливих згадок

---

**Готово! Reddit collector інтегровано в систему! 🎉**

