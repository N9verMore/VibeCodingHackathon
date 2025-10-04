# 🚀 Quick Reference

## Environment Variables (встановлюються автоматично)

```
Lambda: serpapi-collector-lambda
├── TABLE_NAME = "ReviewsTable"
├── SECRET_NAME = "review-collector/credentials"
└── PYTHONPATH = "/var/task:/var/task/shared"
```

## AWS Secrets Manager (потрібно додати вручну)

```json
{
  "serpapi": {
    "api_key": "your_serpapi_api_key"
  }
}
```

**Команда:**
```bash
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{"serpapi":{"api_key":"YOUR_KEY"}}'
```

---

## Швидкий Старт

### 1. Deploy
```bash
cd cdk
cdk deploy
```

### 2. Додати SerpAPI Key
```bash
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{"serpapi":{"api_key":"YOUR_KEY"}}'
```

### 3. Тест
```bash
./scripts/collect_reviews.sh
```

---

## Способи Запуску

### 1️⃣ Bash Script (інтерактивно)
```bash
./scripts/collect_reviews.sh
```

### 2️⃣ Python CLI
```bash
python scripts/manual_trigger.py \
  --source appstore \
  --app-id 544007664 \
  --brand telegram \
  --limit 50
```

### 3️⃣ HTTP API
```bash
curl -X POST "https://YOUR_API_URL/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 50
  }'
```

### 4️⃣ AWS CLI
```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{"source":"appstore","app_identifier":"544007664","brand":"telegram"}' \
  --cli-binary-format raw-in-base64-out \
  response.json
```

---

## Популярні додатки

### App Store
```bash
# Telegram
--source appstore --app-id 544007664

# WhatsApp  
--source appstore --app-id 310633997

# Instagram
--source appstore --app-id 389801252

# TikTok
--source appstore --app-id 835599320
```

### Google Play
```bash
# Telegram
--source googleplay --app-id org.telegram.messenger

# WhatsApp
--source googleplay --app-id com.whatsapp

# Instagram
--source googleplay --app-id com.instagram.android

# TikTok
--source googleplay --app-id com.zhiliaoapp.musically
```

### Trustpilot
```bash
# Tesla
--source trustpilot --app-id tesla.com

# Amazon
--source trustpilot --app-id amazon.com

# Booking
--source trustpilot --app-id booking.com
```

---

## Корисні Команди

### Перевірити env vars Lambda
```bash
aws lambda get-function-configuration \
  --function-name serpapi-collector-lambda \
  --query 'Environment.Variables'
```

### Перевірити secret
```bash
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials \
  --query SecretString --output text | jq
```

### Подивитись logs
```bash
aws logs tail /aws/lambda/serpapi-collector-lambda --follow
```

### Отримати API URL
```bash
aws cloudformation describe-stacks \
  --stack-name ReviewCollectorStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

### Query reviews з DynamoDB
```bash
aws dynamodb query \
  --table-name ReviewsTable \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand": {"S": "telegram"}}'
```

---

## Файли

```
📁 review_collector/
├── 📄 README.md                    # Загальний огляд
├── 📄 SERPAPI_GUIDE.md            # Повна документація
├── 📄 ENV_VARIABLES.md            # Environment variables
├── 📄 QUICK_REFERENCE.md          # Цей файл
├── 📄 MIGRATION_NOTES.md          # Нотатки про міграцію
│
├── 📁 src/
│   ├── 📁 serpapi_collector/      # Lambda функція
│   └── 📁 shared/                  # Спільна інфраструктура
│
├── 📁 cdk/                         # Infrastructure as Code
│   └── 📁 stacks/
│
└── 📁 scripts/                     # Скрипти
    ├── collect_reviews.sh          # Bash
    └── manual_trigger.py           # Python
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Lambda timeout | Збільшити `timeout` в CDK до 10 хв |
| SerpAPI rate limit | Зачекати 1-2 хв або оновити план |
| Invalid app_id | Перевірити формат (число для App Store) |
| No SerpAPI key | Додати в Secrets Manager |
| Import error | Перевірити `PYTHONPATH` env var |

---

## Вартість

| Сервіс | Місяць |
|--------|--------|
| AWS (Lambda, DynamoDB, API Gateway) | ~$0.70 |
| SerpAPI Free | $0 (100 searches) |
| SerpAPI Basic | $50 (5,000 searches) |
| **Total** | **$0.70 - $50.70** |

---

## Посилання

- 📚 [Повна документація](./SERPAPI_GUIDE.md)
- 🔧 [Environment Variables](./ENV_VARIABLES.md)
- 🔄 [Migration Notes](./MIGRATION_NOTES.md)
- 🌐 [SerpAPI Docs](https://serpapi.com/docs)

---

**Швидка допомога:** Подивіться [SERPAPI_GUIDE.md](./SERPAPI_GUIDE.md) для детальних прикладів! 🚀

