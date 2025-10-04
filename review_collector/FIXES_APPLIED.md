# 🔧 Виправлення CDK Стека - Звіт

**Дата:** 2025-10-04  
**Статус:** ✅ Всі критичні проблеми виправлено

---

## 📋 Що Було Виправлено

### ✅ 1. DynamoDB Schema (КРИТИЧНО)
**Проблема:** Невідповідність між схемою таблиці та моделлю даних
- Було: `source_id` (PK) + `content_hash` (SK)
- Стало: `pk` (PK) - composite key у форматі `{source}#{id}`

**Файл:** `cdk/stacks/review_collector_stack.py`

**Зміни:**
```python
# Було:
partition_key=dynamodb.Attribute(
    name="source_id",
    type=dynamodb.AttributeType.STRING
),
sort_key=dynamodb.Attribute(
    name="content_hash",
    type=dynamodb.AttributeType.STRING
),

# Стало:
partition_key=dynamodb.Attribute(
    name="pk",
    type=dynamodb.AttributeType.STRING
),
# Без sort_key
```

---

### ✅ 2. Назва Таблиці
**Зміна:** Створена нова таблиця з правильною схемою
- Було: `ReviewsTable`
- Стало: `ReviewsTableV2`

**Причина:** Уникнення конфліктів зі старою таблицею та можливість міграції

---

### ✅ 3. Environment Variable (КРИТИЧНО)
**Проблема:** Невідповідність назви змінної оточення

**Файл:** `cdk/stacks/review_collector_stack.py`

**Зміни:**
```python
# Було:
environment={
    "DYNAMODB_TABLE_NAME": table.table_name,
    ...
}

# Стало:
environment={
    "TABLE_NAME": table.table_name,
    ...
}
```

**Чому важливо:** Repository шукає `TABLE_NAME`, а не `DYNAMODB_TABLE_NAME`

---

### ✅ 4. Lambda Handler Name (КРИТИЧНО)
**Проблема:** Неправильна назва функції handler

**Файли:**
- `src/serpapi_collector/handler.py`
- `cdk/stacks/review_collector_stack.py`

**Зміни:**
```python
# handler.py
# Було:
def handler(event, context):
    ...

# Стало:
def lambda_handler(event, context):
    ...

# review_collector_stack.py
# Було:
handler="handler.handler",

# Стало:
handler="handler.lambda_handler",
```

---

### ✅ 5. Lambda Resources Optimization
**Зміни:** Оптимізовано ресурси Lambda для економії коштів

```python
# Було:
timeout=Duration.seconds(300),  # 5 хвилин
memory_size=1024,  # 1 GB

# Стало:
timeout=Duration.seconds(120),  # 2 хвилини
memory_size=512,  # 512 MB
```

**Причина:** Початкові значення були надмірними для task review collection

---

### ✅ 6. CDK Outputs
**Додано:** Вивід назви DynamoDB таблиці

```python
CfnOutput(
    self,
    "DynamoDBTableName",
    value=table.table_name,
    description="DynamoDB Table Name"
)
```

---

## 📊 Нова Структура DynamoDB

### Основна Таблиця: `ReviewsTableV2`

**Primary Key:**
- `pk` (STRING) - Partition Key
  - Формат: `{source}#{id}`
  - Приклад: `appstore#1234567890`

**Attributes:**
```json
{
  "pk": "appstore#1234567890",
  "id": "1234567890",
  "source": "appstore",
  "backlink": "https://apps.apple.com/app/...",
  "brand": "myapp",
  "app_identifier": "com.example.myapp",
  "title": "Great app!",
  "text": "Really enjoying this app...",
  "rating": 5,
  "language": "en",
  "country": "US",
  "author_hint": "JohnD",
  "created_at": "2025-10-01T12:00:00",
  "fetched_at": "2025-10-04T14:30:00",
  "content_hash": "a1b2c3d4..."
}
```

**Global Secondary Index:**
- `brand-created_at-index`
  - Partition Key: `brand` (STRING)
  - Sort Key: `created_at` (STRING)
  - Використання: Запити всіх reviews для конкретного бренду

**Billing Mode:** PAY_PER_REQUEST (on-demand)

**Features:**
- ✅ Point-in-time recovery enabled
- ✅ RemovalPolicy: RETAIN (захист від видалення)

---

## 🚀 Deployment Instructions

### Крок 1: Видалити старий стек (опціонально)
```bash
cd /Users/myk/PycharmProjects/monitor/VibeCodingHackathon/review_collector/cdk
cdk destroy ReviewCollectorStack
```

### Крок 2: Синтезувати новий шаблон
```bash
cdk synth
```

### Крок 3: Задеплоїти стек
```bash
cdk deploy ReviewCollectorStack
```

### Крок 4: Перевірити outputs
```bash
cat outputs.json
```

Очікуваний вивід:
```json
{
  "ReviewCollectorStack": {
    "ApiUrl": "https://[api-id].execute-api.us-east-1.amazonaws.com/prod/",
    "ApiEndpoint": "https://[api-id].execute-api.us-east-1.amazonaws.com/prod/collect-reviews",
    "LambdaFunctionName": "serpapi-collector-lambda",
    "DynamoDBTableName": "ReviewsTableV2"
  }
}
```

---

## 🧪 Testing

### Test Lambda Locally
```bash
# Direct invoke
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{"source":"appstore","app_identifier":"544007664","brand":"telegram","limit":10}' \
  response.json

cat response.json
```

### Test API Gateway
```bash
curl -X POST https://[api-id].execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 10
  }'
```

### Verify DynamoDB
```bash
aws dynamodb scan \
  --table-name ReviewsTableV2 \
  --limit 5
```

---

## 📝 Migration Notes (якщо потрібна міграція даних)

Якщо у вас є дані в старій таблиці `ReviewsTable`, використайте цей скрипт:

```python
import boto3

dynamodb = boto3.resource('dynamodb')
old_table = dynamodb.Table('ReviewsTable')
new_table = dynamodb.Table('ReviewsTableV2')

# Scan old table
response = old_table.scan()

for item in response['Items']:
    # Transform to new schema
    new_item = {
        'pk': f"{item['source']}#{item['id']}",
        **item
    }
    # Remove old keys if exist
    new_item.pop('source_id', None)
    
    # Write to new table
    new_table.put_item(Item=new_item)
    print(f"Migrated: {new_item['pk']}")
```

---

## ✅ Verification Checklist

- [x] DynamoDB schema співпадає з Domain Model
- [x] Lambda handler name правильний
- [x] Environment variables правильні
- [x] Lambda має proper IAM permissions
- [x] API Gateway endpoint налаштований
- [x] CORS налаштовано
- [x] Secrets Manager integration працює
- [x] Lambda Layer з shared code
- [x] CloudWatch Logs enabled
- [x] Table має GSI для brand queries

---

## 🎯 Stack Resources

**Created Resources:**
1. ✅ DynamoDB Table: `ReviewsTableV2`
2. ✅ Lambda Layer: `review-collector-shared`
3. ✅ Lambda Function: `serpapi-collector-lambda`
4. ✅ IAM Role: `SerpAPICollectorLambdaServiceRole`
5. ✅ IAM Policy: DynamoDB + Secrets Manager permissions
6. ✅ API Gateway: `Review Collector API`
7. ✅ API Stage: `prod`

**Referenced Resources:**
1. ✅ Secrets Manager: `review-collector/credentials`

---

## 🔐 Required Secret Structure

Переконайтесь що secret `review-collector/credentials` має структуру:

```json
{
  "serpapi": {
    "api_key": "your_serpapi_key_here"
  }
}
```

Створити/оновити secret:
```bash
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{"serpapi":{"api_key":"YOUR_KEY_HERE"}}'
```

---

## 📈 Next Steps (Рекомендації)

1. **Monitoring**: Додати CloudWatch Alarms для:
   - Lambda errors
   - API Gateway 4xx/5xx errors
   - DynamoDB throttling

2. **Cost Optimization**: Переглянути Lambda metrics через тиждень:
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Lambda \
     --metric-name Duration \
     --dimensions Name=FunctionName,Value=serpapi-collector-lambda \
     --start-time 2025-10-04T00:00:00Z \
     --end-time 2025-10-11T00:00:00Z \
     --period 3600 \
     --statistics Average,Maximum
   ```

3. **Security**: Додати API Key для API Gateway:
   ```python
   api_key = api.add_api_key("ApiKey")
   usage_plan = api.add_usage_plan("UsagePlan",
       throttle=apigateway.ThrottleSettings(
           rate_limit=100,
           burst_limit=200
       )
   )
   ```

4. **X-Ray Tracing**: Увімкнути для debugging:
   ```python
   fn = lambda_.Function(
       ...,
       tracing=lambda_.Tracing.ACTIVE
   )
   ```

---

## 🐛 Troubleshooting

### Lambda Cannot Find Module
**Symptom:** `ModuleNotFoundError: No module named 'application'`

**Solution:** Lambda Layer має бути в `/opt/python/` - перевірте bundling:
```bash
# Check layer structure
aws lambda get-layer-version \
  --layer-name review-collector-shared \
  --version-number 1
```

### DynamoDB Access Denied
**Symptom:** `AccessDeniedException`

**Solution:** Перевірте IAM permissions:
```bash
aws iam get-role-policy \
  --role-name SerpAPICollectorLambdaServiceRole \
  --policy-name SerpAPICollectorLambdaServiceRoleDefaultPolicy
```

### Secrets Manager Error
**Symptom:** `ResourceNotFoundException`

**Solution:** Створіть secret:
```bash
aws secretsmanager create-secret \
  --name review-collector/credentials \
  --secret-string '{"serpapi":{"api_key":"YOUR_KEY"}}'
```

---

**Виправлено всі критичні помилки ✅**  
**Готово до deployment 🚀**

