# DataForSEO Trustpilot - Quick Start Guide

## 🚀 Швидкий старт

### 1. Локальне тестування

```bash
# Встановити змінні середовища
export DATAFORSEO_LOGIN="mglushko@perfsys.com"
export DATAFORSEO_PASSWORD="cd0bdc42c24cad76"

# Запустити тестовий скрипт
cd VibeCodingHackathon/review_collector
python scripts/test_dataforseo.py \
  --domain www.zara.com \
  --brand zara \
  --limit 40
```

### 2. Використання через Lambda

```bash
# Спочатку додайте credentials у AWS Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "dataforseo": {
      "login": "mglushko@perfsys.com",
      "password": "cd0bdc42c24cad76"
    },
    "serpapi": {
      "api_key": "YOUR_SERPAPI_KEY"
    }
  }'

# Викликати Lambda
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "trustpilot",
    "app_identifier": "www.zara.com",
    "brand": "zara",
    "limit": 40
  }' \
  response.json

# Подивитись результат
cat response.json | jq
```

### 3. Використання через HTTP API

```bash
# POST запит до API Gateway
curl -X POST "https://YOUR_API_URL/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "www.zara.com",
    "brand": "zara",
    "limit": 40
  }'
```

---

## 📝 Приклади app_identifier

### Популярні бренди на Trustpilot

| Бренд | app_identifier | URL |
|-------|----------------|-----|
| Zara | `www.zara.com` | https://www.trustpilot.com/review/www.zara.com |
| Tesla | `www.tesla.com` | https://www.trustpilot.com/review/www.tesla.com |
| Amazon | `www.amazon.com` | https://www.trustpilot.com/review/www.amazon.com |
| Booking.com | `www.booking.com` | https://www.trustpilot.com/review/www.booking.com |
| Uber | `www.uber.com` | https://www.trustpilot.com/review/www.uber.com |
| Airbnb | `www.airbnb.com` | https://www.trustpilot.com/review/www.airbnb.com |

**Як знайти свій domain:**
1. Знайдіть компанію на Trustpilot
2. URL буде виглядати: `https://www.trustpilot.com/review/DOMAIN`
3. Використовуйте `DOMAIN` як `app_identifier`

---

## 🔍 Очікувана поведінка

### Час виконання
- **Створення задачі**: ~0.1 сек
- **Polling (очікування)**: 3-10 сек
- **Отримання результатів**: ~0.2 сек
- **Загальний час**: **5-15 секунд**

### Ліміти
- **Мінімум**: 1 відгук
- **Максимум**: 5000 відгуків за запит
- **Рекомендовано**: 40-100 відгуків

### Вартість (DataForSEO)
- **Task creation**: ~$0.001
- **Per review**: ~$0.001
- **40 reviews**: ~$0.04-$0.05

---

## ✅ Успішний результат

```json
{
  "success": true,
  "message": "Reviews collected successfully",
  "statistics": {
    "brand": "zara",
    "app_identifier": "www.zara.com",
    "fetched": 40,
    "saved": 38,
    "skipped": 2,
    "errors": 0,
    "duplicates": 2,
    "execution_time": "8.5s"
  },
  "request": {
    "source": "trustpilot",
    "app_identifier": "www.zara.com",
    "brand": "zara",
    "limit": 40
  }
}
```

---

## 🐛 Troubleshooting

### Помилка: "Task did not complete within 60 seconds"

**Причина**: Задача занадто довго виконується

**Рішення**:
- Зменшити `limit` (наприклад, з 100 до 40)
- Перевірити статус задачі вручну через API

### Помилка: "401 Unauthorized"

**Причина**: Невірні credentials

**Рішення**:
```bash
# Перевірити credentials
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials \
  --query SecretString \
  --output text | jq .dataforseo
```

### Помилка: "Domain not found on Trustpilot"

**Причина**: Неправильний формат domain або компанії немає на Trustpilot

**Рішення**:
- Використовувати **повний domain** (e.g., `www.zara.com`, а не `zara.com`)
- Перевірити чи існує сторінка на Trustpilot: https://www.trustpilot.com/review/www.zara.com

---

## 📊 Перевірка результатів у DynamoDB

```bash
# Список всіх Trustpilot відгуків для бренду
aws dynamodb query \
  --table-name ReviewsTable \
  --index-name BrandSourceIndex \
  --key-condition-expression "brand = :brand AND begins_with(#src, :source)" \
  --expression-attribute-names '{"#src":"source"}' \
  --expression-attribute-values '{
    ":brand": {"S": "zara"},
    ":source": {"S": "trustpilot"}
  }'

# Кількість відгуків
aws dynamodb query \
  --table-name ReviewsTable \
  --index-name BrandSourceIndex \
  --key-condition-expression "brand = :brand AND begins_with(#src, :source)" \
  --expression-attribute-names '{"#src":"source"}' \
  --expression-attribute-values '{
    ":brand": {"S": "zara"},
    ":source": {"S": "trustpilot"}
  }' \
  --select COUNT
```

---

## 🧪 Додаткові тести

### Тест з різними доменами

```bash
# Telegram
python scripts/test_dataforseo.py --domain www.telegram.org --brand telegram --limit 20

# Nike
python scripts/test_dataforseo.py --domain www.nike.com --brand nike --limit 50

# Apple
python scripts/test_dataforseo.py --domain www.apple.com --brand apple --limit 100
```

### Тест з експортом у JSON

```bash
python scripts/test_dataforseo.py \
  --domain www.zara.com \
  --brand zara \
  --limit 40 \
  --output zara_reviews.json

# Подивитись результат
cat zara_reviews.json | jq '.reviews | length'
cat zara_reviews.json | jq '.reviews[0]'
```

---

## 📚 Детальна документація

Для повної інформації про DataForSEO API дивіться:
- **[DATAFORSEO_GUIDE.md](./DATAFORSEO_GUIDE.md)** - Повний гайд з усіма деталями
- **[API_INSTRUCTIONS.md](./API_INSTRUCTIONS.md)** - Інструкція користувача API

---

**Готово! 🎉 Тепер ви можете збирати відгуки з Trustpilot через DataForSEO API!**

