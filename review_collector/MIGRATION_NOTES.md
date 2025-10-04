# 🔄 Migration Notes: Офіційні API → SerpAPI

## Що було видалено

### Старі Lambda collectors
- ❌ `src/appstore_collector/` - замінено на `serpapi_collector`
- ❌ `src/googleplay_collector/` - замінено на `serpapi_collector`
- ❌ `src/trustpilot_collector/` - замінено на `serpapi_collector`

### Старі скрипти
- ❌ `scripts/setup_placeholder_credentials.sh` - більше не потрібен
- ❌ `scripts/update_credentials.sh` - більше не потрібен
- ❌ `scripts/credentials.json.example` - замінено на простішу структуру

### Старі CDK artifacts
- ❌ `cdk/cdk.out/` - буде перегенеровано при deploy

---

## Нова структура

```
review_collector/
├── src/
│   ├── serpapi_collector/        # ✅ НОВИЙ - unified collector
│   └── shared/                   # ✅ Залишився без змін
├── scripts/
│   ├── collect_reviews.sh        # ✅ НОВИЙ - інтерактивне меню
│   └── manual_trigger.py         # ✅ НОВИЙ - Python CLI
├── cdk/                          # ✅ Оновлений для API Gateway
├── SERPAPI_GUIDE.md             # ✅ НОВИЙ - повна документація
└── README.md                     # ✅ Оновлений
```

---

## Що потрібно зробити після git pull

### 1. Оновити Secrets Manager

Старий формат:
```json
{
  "appstore": {"key_id": "...", "issuer_id": "...", "private_key": "..."},
  "googleplay": {...},
  "trustpilot": {"api_key": "..."}
}
```

Новий формат (додати):
```json
{
  "serpapi": {
    "api_key": "your_serpapi_key"
  }
}
```

Команда:
```bash
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{"serpapi":{"api_key":"YOUR_KEY"}}'
```

### 2. Redeploy CDK

```bash
cd cdk
cdk destroy  # Видалити старий stack (опціонально)
cdk deploy   # Задеплоїти новий
```

### 3. Видалити старі Lambda functions (якщо залишились)

```bash
aws lambda delete-function --function-name appstore-collector-lambda
aws lambda delete-function --function-name googleplay-collector-lambda
aws lambda delete-function --function-name trustpilot-collector-lambda
```

### 4. Видалити старі EventBridge rules (якщо були)

```bash
aws events list-rules --name-prefix "appstore-"
aws events delete-rule --name appstore-daily-schedule
# Повторити для googleplay та trustpilot
```

---

## Breaking Changes

### API
- **Старе:** 3 окремі Lambda functions з hardcoded APP_IDENTIFIER
- **Нове:** 1 unified Lambda + API Gateway з dynamic parameters

### Credentials
- **Старе:** Окремі credentials для кожної платформи
- **Нове:** Один SerpAPI key

### Invocation
- **Старе:** Тільки EventBridge schedule
- **Нове:** HTTP API + Direct invoke + Schedule (опціонально)

---

## Compatibility

### ✅ Залишається без змін:
- DynamoDB schema
- Review entity structure
- Shared infrastructure (domain, repositories, use cases)
- Ідемпотентність (content_hash)

### ⚠️ Потрібна увага:
- Якщо використовували офіційні API credentials - вони більше не потрібні
- Якщо були scheduled jobs - потрібно оновити на нову Lambda function

---

## Rollback Plan

Якщо потрібно повернутися до старої версії:

```bash
# 1. Checkout старий код
git checkout <old_commit>

# 2. Redeploy старий stack
cd cdk
cdk deploy

# 3. Відновити старі credentials в Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{...old_credentials...}'
```

---

**Дата міграції:** 2024-10-04  
**Версія:** 2.0.0 (SerpAPI)

