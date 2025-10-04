# Environment Variables

## Lambda Function (автоматично встановлюються CDK)

Lambda function `serpapi-collector-lambda` використовує наступні environment variables:

### 1. `TABLE_NAME` (обов'язково)
- **Опис:** Ім'я DynamoDB таблиці для зберігання відгуків
- **Значення:** `ReviewsTable` (встановлюється автоматично CDK)
- **Використання:** `DynamoDBReviewRepository` використовує цю змінну для з'єднання з таблицею

```python
# В коді:
table_name = os.environ.get('TABLE_NAME', 'ReviewsTable')
```

### 2. `SECRET_NAME` (обов'язково)
- **Опис:** Ім'я секрету в AWS Secrets Manager з API credentials
- **Значення:** `review-collector/credentials` (встановлюється автоматично CDK)
- **Використання:** `SecretsClient` витягує SerpAPI key з цього секрету

```python
# В коді:
secret_name = os.environ.get('SECRET_NAME', 'review-collector/credentials')
```

### 3. `PYTHONPATH` (автоматично)
- **Опис:** Python module search path для Lambda
- **Значення:** `/var/task:/var/task/shared`
- **Використання:** Дозволяє імпортувати `shared` модулі з `serpapi_collector`

```python
# В коді:
from ..shared import CollectReviewsUseCase
```

### 4. `AWS_REGION` (автоматично Lambda)
- **Опис:** AWS регіон де виконується Lambda
- **Значення:** Встановлюється автоматично AWS Lambda runtime
- **Використання:** Використовується boto3 для з'єднання з DynamoDB і Secrets Manager

---

## CDK Deployment (встановлюються в stack)

```python
# cdk/stacks/review_collector_stack.py
environment={
    "TABLE_NAME": table.table_name,        # ReviewsTable
    "SECRET_NAME": secret.secret_name,     # review-collector/credentials
    "PYTHONPATH": "/var/task:/var/task/shared"
}
```

---

## AWS Secrets Manager (потрібно налаштувати вручну)

### Secret: `review-collector/credentials`

**Структура JSON:**
```json
{
  "serpapi": {
    "api_key": "your_serpapi_api_key_here"
  }
}
```

**Як встановити:**
```bash
# Створити/оновити secret
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {
      "api_key": "YOUR_SERPAPI_KEY"
    }
  }'
```

**Як перевірити:**
```bash
# Подивитись secret
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials \
  --query SecretString \
  --output text | jq
```

---

## Локальна Розробка (опціонально)

Якщо хочете тестувати Lambda локально, встановіть:

```bash
# Встановити env vars
export TABLE_NAME=ReviewsTable
export SECRET_NAME=review-collector/credentials
export AWS_REGION=us-east-1
export AWS_PROFILE=your-aws-profile  # якщо використовуєте named profile

# Або створити .env файл
cat > .env << EOF
TABLE_NAME=ReviewsTable
SECRET_NAME=review-collector/credentials
AWS_REGION=us-east-1
EOF

# Завантажити в shell
source .env
```

**Тестування локально:**
```python
# test_local.py
import os
os.environ['TABLE_NAME'] = 'ReviewsTable'
os.environ['SECRET_NAME'] = 'review-collector/credentials'

from src.serpapi_collector.handler import handler

event = {
    'source': 'appstore',
    'app_identifier': '544007664',
    'brand': 'telegram',
    'limit': 10
}

response = handler(event, None)
print(response)
```

---

## Скрипти (не потребують env vars)

### `scripts/collect_reviews.sh`
```bash
# Використовує AWS CLI credentials з профілю
# Не потребує env vars, все передається через аргументи
./scripts/collect_reviews.sh
```

### `scripts/manual_trigger.py`
```bash
# Використовує boto3 credentials (AWS_PROFILE або default)
python scripts/manual_trigger.py \
  --source appstore \
  --app-id 544007664 \
  --brand telegram
```

**Опціональні параметри:**
```bash
--region us-east-1              # AWS region (default: us-east-1)
--function-name lambda-name     # Lambda function name
```

---

## Перевірка Environment Variables

### В Lambda Console:
1. Відкрити: https://console.aws.amazon.com/lambda
2. Знайти функцію: `serpapi-collector-lambda`
3. Configuration → Environment variables
4. Перевірити наявність:
   - `TABLE_NAME`
   - `SECRET_NAME`
   - `PYTHONPATH`

### Через AWS CLI:
```bash
# Подивитись всі env vars Lambda
aws lambda get-function-configuration \
  --function-name serpapi-collector-lambda \
  --query 'Environment.Variables'
```

**Expected output:**
```json
{
  "TABLE_NAME": "ReviewsTable",
  "SECRET_NAME": "review-collector/credentials",
  "PYTHONPATH": "/var/task:/var/task/shared"
}
```

---

## IAM Permissions (автоматично через CDK)

Lambda автоматично отримує permissions через CDK:

```python
# DynamoDB access
table.grant_read_write_data(fn)

# Secrets Manager access
secret.grant_read(fn)
```

**Результат:**
- ✅ `dynamodb:GetItem`
- ✅ `dynamodb:PutItem`
- ✅ `dynamodb:Query`
- ✅ `secretsmanager:GetSecretValue`

---

## Troubleshooting

### Problem: Lambda не може прочитати secret

**Error:**
```
ValueError: SerpAPI credentials not found in secret
```

**Solution:**
```bash
# Перевірити SECRET_NAME
aws lambda get-function-configuration \
  --function-name serpapi-collector-lambda \
  --query 'Environment.Variables.SECRET_NAME'

# Перевірити що secret існує
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials
```

### Problem: Lambda не може писати в DynamoDB

**Error:**
```
AccessDeniedException: User is not authorized to perform: dynamodb:PutItem
```

**Solution:**
```bash
# Перевірити IAM permissions Lambda
aws lambda get-policy \
  --function-name serpapi-collector-lambda
```

### Problem: Import error для shared modules

**Error:**
```
ModuleNotFoundError: No module named 'shared'
```

**Solution:**
```bash
# Перевірити PYTHONPATH
aws lambda get-function-configuration \
  --function-name serpapi-collector-lambda \
  --query 'Environment.Variables.PYTHONPATH'

# Має бути: /var/task:/var/task/shared
```

---

## Summary

### Автоматично (CDK):
- ✅ `TABLE_NAME`
- ✅ `SECRET_NAME`
- ✅ `PYTHONPATH`
- ✅ IAM Permissions

### Вручну (один раз):
- ⚠️ AWS Secrets Manager: додати SerpAPI key

### Не потрібно:
- ❌ API credentials в env vars (зберігаються в Secrets Manager)
- ❌ Hardcoded app identifiers (передаються в request)
- ❌ Brand names (передаються в request)

---

**Все налаштовується автоматично через `cdk deploy`! 🚀**

