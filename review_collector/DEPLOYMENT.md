да# 🚀 Deployment Guide

Покроковий посібник для деплою Review Collector без API ключів (з можливістю додати їх пізніше).

---

## 📋 Передумови

1. ✅ AWS CLI налаштований (`aws configure`)
2. ✅ Python 3.12+ встановлений
3. ✅ Node.js 18+ встановлений
4. ✅ AWS CDK встановлений: `npm install -g aws-cdk`

---

## 🎯 Етап 1: Деплой інфраструктури (БЕЗ API ключів)

### Крок 1.1: Створити placeholder credentials

```bash
cd review_collector
./scripts/setup_placeholder_credentials.sh
```

Це створить секрет з placeholder значеннями, щоб Lambda не падали при ініціалізації.

### Крок 1.2: Встановити CDK залежності

```bash
cd cdk
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Крок 1.3: Bootstrap CDK (тільки перший раз)

```bash
cdk bootstrap
```

### Крок 1.4: Деплой stack

```bash
cdk deploy
```

Підтвердіть створення IAM ролей коли буде запит (введіть `y`).

### ✅ Що створено?

- ✅ **DynamoDB Table**: `ReviewsTable`
- ✅ **Lambda Functions** (x3): 
  - `appstore-collector-lambda`
  - `googleplay-collector-lambda`
  - `trustpilot-collector-lambda`
- ✅ **Secrets Manager**: `review-collector/credentials` (з placeholder значеннями)
- ✅ **IAM Roles** з необхідними правами
- ✅ **CloudWatch Logs** groups

⚠️ **EventBridge schedulers закоментовані** - Lambda не запускатимуться автоматично до додавання реальних ключів.

---

## 🔑 Етап 2: Додати API ключі (коли отримаєте)

### Крок 2.1: Створити файл з credentials

Скопіюйте приклад:
```bash
cd review_collector
cp scripts/credentials.json.example credentials.json
```

Відредагуйте `credentials.json` з реальними ключами:
```json
{
  "appstore": {
    "key_id": "ABC123DEFG",
    "issuer_id": "12345678-1234-1234-1234-123456789012",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
  },
  "googleplay": {
    "type": "service_account",
    "project_id": "your-project-123456",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "service@project.iam.gserviceaccount.com"
  },
  "trustpilot": {
    "api_key": "your-api-key"
  }
}
```

### Крок 2.2: Оновити credentials в AWS

```bash
./scripts/update_credentials.sh credentials.json
```

### Крок 2.3: Налаштувати параметри додатків

Відредагуйте `cdk/stacks/review_collector_stack.py`:

```python
# Line 55-57
app_identifier="1234567890",  # Ваш Apple App ID
brand="YOUR_BRAND"

# Line 64-66
app_identifier="com.example.app",  # Ваш package name
brand="YOUR_BRAND"

# Line 73-75
app_identifier="your-business-unit-id",  # Ваш Trustpilot ID
brand="YOUR_BRAND"
```

### Крок 2.4: Увімкнути schedulers

Розкоментуйте рядки 78-102 в `cdk/stacks/review_collector_stack.py`:

```python
# Видаліть коментарі з:
schedule_expression = events.Schedule.cron(...)
self._create_scheduler(...)
```

### Крок 2.5: Передеплоїти

```bash
cd cdk
cdk deploy
```

---

## ✅ Етап 3: Тестування

### Ручний запуск Lambda

```bash
# Test App Store collector
aws lambda invoke \
  --function-name appstore-collector-lambda \
  --payload '{}' \
  response.json

cat response.json
```

### Перевірка логів

```bash
# Real-time logs
aws logs tail /aws/lambda/appstore-collector-lambda --follow

# Last 10 minutes
aws logs tail /aws/lambda/appstore-collector-lambda --since 10m
```

### Query DynamoDB

```bash
# Scan all reviews
aws dynamodb scan \
  --table-name ReviewsTable \
  --limit 10

# Query by brand
aws dynamodb query \
  --table-name ReviewsTable \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand": {"S": "YOUR_BRAND"}}'
```

---

## 🔄 Оновлення коду

Якщо змінили код Lambda:

```bash
cd cdk
cdk deploy
```

CDK автоматично перезаллє тільки змінені Lambda functions.

---

## 🧹 Видалення stack

⚠️ **УВАГА**: Це видалить Lambda та schedulers, але **НЕ** видалить:
- DynamoDB table (RetentionPolicy.RETAIN)
- Secrets Manager secret (RetentionPolicy.RETAIN)

```bash
cd cdk
cdk destroy
```

Щоб видалити все (включно з даними):
```bash
# Delete DynamoDB table
aws dynamodb delete-table --table-name ReviewsTable

# Delete secret
aws secretsmanager delete-secret \
  --secret-id review-collector/credentials \
  --force-delete-without-recovery
```

---

## 🐛 Troubleshooting

### Lambda timeout
```python
# В review_collector_stack.py, line 149
timeout=Duration.minutes(10),  # Збільште з 5 до 10
```

### Memory issues
```python
# В review_collector_stack.py, line 150
memory_size=1024,  # Збільште з 512 до 1024
```

### CDK bootstrap issues
```bash
# Перевірте region
echo $AWS_DEFAULT_REGION

# Bootstrap для specific region
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### Credentials not working
```bash
# Перевірте секрет
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials \
  --query SecretString \
  --output text | jq .

# Перевірте Lambda env vars
aws lambda get-function-configuration \
  --function-name appstore-collector-lambda
```

---

## 📊 Моніторинг

### CloudWatch Dashboards

Можна створити дашборд для моніторингу:
- Lambda invocations
- Errors
- Duration
- DynamoDB read/write capacity

### Алерти

Налаштуйте SNS topics для алертів при:
- Lambda errors > 5/hour
- Lambda duration > 4 minutes
- DynamoDB throttling

---

## 💰 Вартість

Приблизна вартість на місяць:
- Lambda: $0.02 (3 x 5min x 30 днів)
- DynamoDB: $0.25 (1000 reviews)
- Secrets Manager: $0.40
- CloudWatch Logs: $0.50
- **Total: ~$1.20/міс**

---

**Готово! 🎉** Lambda functions створені і готові до роботи після додавання API ключів.

