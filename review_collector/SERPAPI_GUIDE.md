# 🚀 SerpAPI Review Collector - Повний Гайд

Збір відгуків з **будь-якого додатку** через SerpAPI - без потреби в офіційних API ключах!

---

## 🎯 Що це дає?

| Можливість | Старе рішення | Нове (SerpAPI) |
|-----------|--------------|----------------|
| **Збір своїх додатків** | ✅ | ✅ |
| **Збір чужих додатків** | ❌ | ✅ |
| **API credentials** | Окремі для кожної платформи | Один SerpAPI key |
| **On-demand збір** | ❌ | ✅ |
| **App ID в коді** | Hardcoded | Dynamic в request |

---

## 📋 Швидкий Старт

### 1. Отримати SerpAPI Key

```bash
# Зареєструватись на SerpAPI
https://serpapi.com/users/sign_up

# Отримати API key з dashboard
https://serpapi.com/manage-api-key
```

**Плани:**
- Free: 100 пошуків/місяць
- Basic: 5,000 пошуків/міс ($50)
- Pro: 15,000 пошуків/міс ($130)

### 2. Додати Key в AWS Secrets Manager

```bash
# Створити/оновити secret
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {
      "api_key": "your_serpapi_key_here"
    }
  }'
```

### 3. Задеплоїти CDK Stack

```bash
cd cdk

# Встановити залежності (якщо ще не встановлено)
pip install -r requirements.txt

# Deploy
cdk deploy

# Зберегти output (API URL)
export API_URL=$(aws cloudformation describe-stacks \
  --stack-name ReviewCollectorStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

echo "API URL: $API_URL"
```

---

## 🎮 Способи Запуску

### Спосіб 1: HTTP API (curl)

```bash
# Telegram з App Store
curl -X POST "${API_URL}collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 50
  }'

# WhatsApp з Google Play
curl -X POST "${API_URL}collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "googleplay",
    "app_identifier": "com.whatsapp",
    "brand": "whatsapp",
    "limit": 100
  }'

# Trustpilot reviews
curl -X POST "${API_URL}collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "tesla.com",
    "brand": "tesla",
    "limit": 20
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Reviews collected successfully",
  "statistics": {
    "fetched": 50,
    "saved": 48,
    "skipped": 2,
    "duration_seconds": 5.3
  },
  "input": {
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 50
  }
}
```

### Спосіб 2: Bash Script (Interactive)

```bash
# Запустити інтерактивне меню
./scripts/collect_reviews.sh

# Вибрати опцію:
# 1) Telegram (App Store)
# 2) WhatsApp (Google Play)
# 3) Instagram (App Store)
# 4) Custom app
```

### Спосіб 3: Python Script

```bash
# Telegram з App Store
python scripts/manual_trigger.py \
  --source appstore \
  --app-id 544007664 \
  --brand telegram \
  --limit 50

# WhatsApp з Google Play
python scripts/manual_trigger.py \
  --source googleplay \
  --app-id com.whatsapp \
  --brand whatsapp \
  --limit 100

# Допомога
python scripts/manual_trigger.py --help
```

### Спосіб 4: AWS CLI (Direct Invoke)

```bash
# Direct Lambda invoke
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 50
  }' \
  --cli-binary-format raw-in-base64-out \
  response.json

# Подивитись результат
cat response.json | jq
```

### Спосіб 5: AWS Lambda Console

1. Відкрити: https://console.aws.amazon.com/lambda
2. Знайти функцію: `serpapi-collector-lambda`
3. Натиснути **Test** → **Configure test event**
4. Вставити JSON:
   ```json
   {
     "source": "appstore",
     "app_identifier": "544007664",
     "brand": "telegram",
     "limit": 50
   }
   ```
5. Натиснути **Test**

---

## 📱 Приклади Додатків

### App Store

| App | App ID | Command |
|-----|--------|---------|
| Telegram | `544007664` | `--source appstore --app-id 544007664` |
| WhatsApp | `310633997` | `--source appstore --app-id 310633997` |
| Instagram | `389801252` | `--source appstore --app-id 389801252` |
| TikTok | `835599320` | `--source appstore --app-id 835599320` |

**Як знайти App ID:**
```
URL: https://apps.apple.com/app/idXXXXXXXXX
App ID: XXXXXXXXX (числовий ID після "id")
```

### Google Play

| App | Package Name | Command |
|-----|--------------|---------|
| Telegram | `org.telegram.messenger` | `--source googleplay --app-id org.telegram.messenger` |
| WhatsApp | `com.whatsapp` | `--source googleplay --app-id com.whatsapp` |
| Instagram | `com.instagram.android` | `--source googleplay --app-id com.instagram.android` |
| TikTok | `com.zhiliaoapp.musically` | `--source googleplay --app-id com.zhiliaoapp.musically` |

**Як знайти Package Name:**
```
URL: https://play.google.com/store/apps/details?id=PACKAGE_NAME
Package Name: PACKAGE_NAME (після "id=")
```

### Trustpilot

| Company | Domain | Command |
|---------|--------|---------|
| Tesla | `tesla.com` | `--source trustpilot --app-id tesla.com` |
| Amazon | `amazon.com` | `--source trustpilot --app-id amazon.com` |
| Booking | `booking.com` | `--source trustpilot --app-id booking.com` |

---

## 🔍 API Reference

### Endpoint

```
POST /collect-reviews
```

### Request Body

```json
{
  "source": "appstore | googleplay | trustpilot",
  "app_identifier": "string (App ID / Package Name / Domain)",
  "brand": "string (brand identifier)",
  "limit": 100  // optional, default: 100
}
```

### Response (Success)

```json
{
  "statusCode": 200,
  "body": {
    "success": true,
    "message": "Reviews collected successfully",
    "statistics": {
      "brand": "telegram",
      "app_identifier": "544007664",
      "fetched": 50,
      "saved": 48,
      "skipped": 2,
      "errors": 0,
      "duration_seconds": 5.3,
      "start_time": "2024-10-04T10:00:00",
      "end_time": "2024-10-04T10:00:05"
    },
    "input": {
      "source": "appstore",
      "app_identifier": "544007664",
      "brand": "telegram",
      "limit": 50
    }
  }
}
```

### Response (Error)

```json
{
  "statusCode": 400,
  "body": {
    "success": false,
    "error": "Validation error",
    "message": "Missing required field: 'source'"
  }
}
```

---

## 🐍 Python SDK Usage

```python
import requests

class ReviewCollectorClient:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def collect_reviews(self, source, app_id, brand, limit=100):
        """Collect reviews from any app"""
        response = requests.post(
            f"{self.api_url}/collect-reviews",
            json={
                'source': source,
                'app_identifier': app_id,
                'brand': brand,
                'limit': limit
            }
        )
        return response.json()

# Usage
client = ReviewCollectorClient(API_URL)

# Telegram reviews
stats = client.collect_reviews('appstore', '544007664', 'telegram', 50)
print(f"Collected {stats['statistics']['saved']} reviews")

# WhatsApp reviews
stats = client.collect_reviews('googleplay', 'com.whatsapp', 'whatsapp', 100)
```

---

## 🔧 Troubleshooting

### Problem: "SerpAPI credentials not found"

**Solution:**
```bash
# Перевірити secret
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials

# Додати SerpAPI key
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{"serpapi":{"api_key":"YOUR_KEY"}}'
```

### Problem: Lambda timeout

**Solution:**
```python
# In CDK stack, збільшити timeout
timeout=Duration.minutes(10)  # було 5
```

### Problem: Rate limit від SerpAPI

**Response:**
```json
{
  "error": "You have reached your rate limit"
}
```

**Solution:**
- Зачекати 1-2 хвилини
- Оновити план на SerpAPI
- Додати затримку між запитами

### Problem: Invalid app_identifier

**Solution:**
- App Store: Використовувати числовий ID (не bundle ID)
- Google Play: Використовувати package name (з крапками)
- Trustpilot: Використовувати domain name

---

## 💰 Вартість

### AWS

| Сервіс | Використання | Ціна/місяць |
|--------|-------------|-------------|
| Lambda | 100 викликів × 5 хв | ~$0.05 |
| DynamoDB | 1000 reviews | ~$0.25 |
| API Gateway | 1000 requests | ~$0.01 |
| Secrets Manager | 1 secret | $0.40 |
| **AWS Total** | | **~$0.70** |

### SerpAPI

| План | Searches/міс | Ціна |
|------|-------------|------|
| Free | 100 | $0 |
| Basic | 5,000 | $50 |
| Pro | 15,000 | $130 |

**Total:** $0.70 (AWS) + $0-130 (SerpAPI) = **$0.70-130/місяць**

---

## 🎯 Use Cases

### 1. Competitor Analysis
```bash
# Збір відгуків конкурентів
python scripts/manual_trigger.py --source appstore --app-id COMPETITOR_ID --brand competitor
```

### 2. Multi-App Monitoring
```python
# Batch збір
apps = [
    ('appstore', '544007664', 'telegram'),
    ('googleplay', 'com.whatsapp', 'whatsapp'),
    ('trustpilot', 'tesla.com', 'tesla')
]

for source, app_id, brand in apps:
    collector.collect_reviews(source, app_id, brand, 50)
```

### 3. Research & Analysis
```bash
# Зібрати reviews для дослідження
curl -X POST "$API_URL/collect-reviews" -d '{
  "source": "appstore",
  "app_identifier": "544007664",
  "brand": "research-telegram",
  "limit": 200
}'
```

---

## 📊 Data Structure

Reviews зберігаються в DynamoDB:

```json
{
  "pk": "appstore#abc123",
  "id": "abc123",
  "source": "appstore",
  "backlink": "https://apps.apple.com/app/id544007664",
  "brand": "telegram",
  "app_identifier": "544007664",
  "title": "Great app!",
  "text": "Best messaging app ever...",
  "rating": 5,
  "language": "en",
  "country": "US",
  "author_hint": "John D.",
  "created_at": "2024-10-01T12:00:00",
  "fetched_at": "2024-10-04T10:00:00",
  "content_hash": "sha256..."
}
```

Query reviews:
```bash
aws dynamodb query \
  --table-name ReviewsTable \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand": {"S": "telegram"}}'
```

---

## 🚀 Next Steps

1. ✅ Задеплоїти stack: `cdk deploy`
2. ✅ Додати SerpAPI key в Secrets Manager
3. ✅ Протестувати API: `./scripts/collect_reviews.sh`
4. 📊 Зібрати перші відгуки
5. 📈 Налаштувати моніторинг конкурентів

---

## 📚 Корисні Посилання

- [SerpAPI Documentation](https://serpapi.com/docs)
- [SerpAPI App Store API](https://serpapi.com/apple-app-store)
- [SerpAPI Google Play API](https://serpapi.com/google-play)
- [SerpAPI Trustpilot API](https://serpapi.com/trustpilot)
- [AWS Lambda Docs](https://docs.aws.amazon.com/lambda/)
- [AWS CDK Docs](https://docs.aws.amazon.com/cdk/)

---

**Built with ❤️ using SerpAPI, AWS Lambda, and Python**

