# DataForSEO API Integration Guide

## Огляд

DataForSEO API використовується для збору відгуків з Trustpilot. На відміну від SerpAPI, DataForSEO використовує **асинхронну модель** з трьома основними кроками:

1. **Створення задачі** (`task_post`) - ініціювання збору даних
2. **Перевірка готовності** (`tasks_ready`) - polling до завершення
3. **Отримання результатів** (`task_get`) - завантаження зібраних відгуків

---

## Авторизація

DataForSEO використовує **Basic Authentication**.

### Credentials
- **Login**: `mglushko@perfsys.com`
- **Password**: `cd0bdc42c24cad76`
- **Base64**: `bWdsdXNoa29AcGVyZnN5cy5jb206Y2QwYmRjNDJjMjRjYWQ3Ng==`

### Використання в запитах
```bash
--header "Authorization: Basic bWdsdXNoa29AcGVyZnN5cy5jb206Y2QwYmRjNDJjMjRjYWQ3Ng=="
```

---

## API Endpoints

### Base URL
```
https://api.dataforseo.com/v3/business_data/trustpilot/reviews
```

### 1. Створення задачі

**Endpoint**: `POST /task_post`

**Request**:
```bash
curl --location --request POST \
  "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/task_post" \
  --header "Authorization: Basic bWdsdXNoa29AcGVyZnN5cy5jb206Y2QwYmRjNDJjMjRjYWQ3Ng==" \
  --header "Content-Type: application/json" \
  --data-raw '[
    {
      "domain": "www.zara.com",
      "depth": 40,
      "sort_by": "recency",
      "priority": 1,
      "tag": "zara_reviews_task"
    }
  ]'
```

**Parameters**:
- `domain` (required): Trustpilot domain (e.g., "www.zara.com")
- `depth` (optional): Number of reviews to collect
  - Default: 20
  - Maximum: 25,000
  - **⚠️ Рекомендація**: Використовувати кратні 20 (20, 40, 60, 100...)
  - **Біллінг**: За кожні 20 відгуків (1 SERP)
  - Наш клієнт автоматично округляє до кратних 20
- `sort_by` (optional): Sort order - "recency" or "rating" (default: "recency")
- `priority` (optional): Task priority - 1 (normal) or 2 (high) (default: 1)
- `tag` (optional): Custom tag for tracking

**Response**:
```json
{
  "version": "0.1.20240801",
  "status_code": 20000,
  "status_message": "Ok.",
  "time": "0.1234 sec.",
  "cost": 0.001,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [
    {
      "id": "10041707-1172-0358-0000-fb7a2c4b0e7f",
      "status_code": 20100,
      "status_message": "Task Created.",
      "time": "0.0123 sec.",
      "cost": 0.001
    }
  ]
}
```

**Key Fields**:
- `tasks[0].id` - Task ID для polling і отримання результатів
- `tasks[0].status_code` - 20100 = успішно створено

---

### 2. Перевірка готовності

**Endpoint**: `GET /tasks_ready`

**Request**:
```bash
curl --location --request GET \
  "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/tasks_ready" \
  --header "Authorization: Basic bWdsdXNoa29AcGVyZnN5cy5jb206Y2QwYmRjNDJjMjRjYWQ3Ng=="
```

**Response** (коли задача готова):
```json
{
  "status_code": 20000,
  "status_message": "Ok.",
  "time": "0.0234 sec.",
  "cost": 0,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [
    {
      "id": "11011442-2806-0357-0000-87f90d2ac78d",
      "status_code": 20000,
      "status_message": "Ok.",
      "time": "0.0910 sec.",
      "cost": 0,
      "result_count": 4,
      "path": ["v3", "business_data", "trustpilot", "reviews", "tasks_ready"],
      "data": {
        "api": "business_data",
        "function": "reviews",
        "se": "trustpilot"
      },
      "result": [
        {
          "id": "10041707-1172-0358-0000-fb7a2c4b0e7f",
          "se": "trustpilot",
          "se_type": "reviews",
          "date_posted": "2021-11-01 11:25:06 +00:00",
          "tag": "trustpilot_www.zara.com",
          "endpoint": "/v3/business_data/trustpilot/reviews/task_get/10041707-1172-0358-0000-fb7a2c4b0e7f"
        }
      ]
    }
  ]
}
```

**⚠️ Важливо про структуру відповіді:**
- Готові задачі знаходяться в `tasks[0].result[]` (а не в `tasks[]`)
- Треба перевіряти `tasks[0].result[].id` для пошуку вашої задачі
- Згідно з [офіційною документацією DataForSEO](https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/tasks_ready/)

**Polling Strategy**:
- Перевіряти кожні 2-3 секунди
- Maximum 20 спроб (60 секунд)
- Задача готова, коли її `id` з'являється в `tasks[0].result[]`

---

### 3. Отримання результатів

**Endpoint**: `GET /task_get/{task_id}`

**Request**:
```bash
curl --location --request GET \
  "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/task_get/10041707-1172-0358-0000-fb7a2c4b0e7f" \
  --header "Authorization: Basic bWdsdXNoa29AcGVyZnN5cy5jb206Y2QwYmRjNDJjMjRjYWQ3Ng=="
```

**Response**:
```json
{
  "status_code": 20000,
  "status_message": "Ok.",
  "time": "0.1567 sec.",
  "cost": 0.05,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [
    {
      "id": "10041707-1172-0358-0000-fb7a2c4b0e7f",
      "status_code": 20000,
      "status_message": "Ok.",
      "time": "5.2345 sec.",
      "cost": 0.05,
      "result_count": 1,
      "path": [...],
      "data": {...},
      "result": [
        {
          "domain": "www.zara.com",
          "type": "trustpilot_reviews",
          "se_domain": "www.trustpilot.com",
          "location_code": null,
          "language_code": null,
          "check_url": "https://www.trustpilot.com/review/www.zara.com",
          "datetime": "2024-10-04 12:34:56 +00:00",
          "items_count": 40,
          "items": [
            {
              "type": "review",
              "rank_group": 1,
              "rank_absolute": 1,
              "position": "left",
              "title": "Excellent service",
              "review_text": "I had a great experience with Zara...",
              "publication_date": "2024-10-01 12:34:56 +00:00",
              "rating": {
                "value": 5,
                "max": 5
              },
              "author": {
                "name": "John D.",
                "url": "https://www.trustpilot.com/users/...",
                "thumbnail": "https://...",
                "number_of_reviews": 5
              },
              "url": "https://www.trustpilot.com/reviews/..."
            }
          ]
        }
      ]
    }
  ]
}
```

**Review Item Structure**:
- `title` - заголовок відгуку
- `review_text` - текст відгуку
- `rating.value` - оцінка (1-5)
- `publication_date` - дата публікації
- `author.name` - ім'я автора
- `url` - посилання на відгук

---

## Python Implementation

### Клас: `DataForSEOTrustpilotClient`

**Location**: `src/serpapi_collector/dataforseo_trustpilot_client.py`

**Initialization**:
```python
from dataforseo_trustpilot_client import DataForSEOTrustpilotClient

client = DataForSEOTrustpilotClient(
    login="mglushko@perfsys.com",
    password="cd0bdc42c24cad76",
    timeout=30,
    max_poll_attempts=20,
    poll_interval=3
)
```

**Usage**:
```python
reviews = client.fetch_reviews(
    app_identifier="www.zara.com",
    brand="zara",
    limit=40
)

print(f"Fetched {len(reviews)} reviews")
for review in reviews:
    print(f"{review.rating}⭐ - {review.title}")
```

**Key Methods**:
- `_create_task(domain, depth)` - створює задачу збору
- `_wait_for_task(task_id)` - чекає завершення
- `_get_results(task_id)` - отримує результати
- `_normalize_review(raw_data, brand, app_identifier)` - нормалізує у `Review` entity

---

## AWS Secrets Manager Configuration

### Secret Name
```
review-collector/credentials
```

### Secret Structure
```json
{
  "dataforseo": {
    "login": "mglushko@perfsys.com",
    "password": "cd0bdc42c24cad76"
  },
  "serpapi": {
    "api_key": "your_serpapi_key"
  }
}
```

### Setting Secret
```bash
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "dataforseo": {
      "login": "mglushko@perfsys.com",
      "password": "cd0bdc42c24cad76"
    }
  }'
```

---

## Testing

### Local Test Script

**Location**: `scripts/test_dataforseo.py`

**Usage**:
```bash
# Set credentials
export DATAFORSEO_LOGIN="mglushko@perfsys.com"
export DATAFORSEO_PASSWORD="cd0bdc42c24cad76"

# Run test
cd review_collector
python scripts/test_dataforseo.py \
  --domain www.zara.com \
  --brand zara \
  --limit 40

# Save results to file
python scripts/test_dataforseo.py \
  --domain www.tesla.com \
  --brand tesla \
  --limit 100 \
  --output tesla_reviews.json
```

**Expected Output**:
```
============================================================
🧪 DataForSEO Trustpilot API Test
============================================================
Domain: www.zara.com
Brand: zara
Limit: 40
Login: mglushko@perfsys.com
============================================================

🔧 Initializing DataForSEO client...
✅ Client initialized

🚀 Fetching reviews for www.zara.com...
📤 Creating task for domain=www.zara.com, depth=40
✅ Task created successfully: 10041707-1172-0358-0000-fb7a2c4b0e7f
⏳ Waiting for task 10041707-1172-0358-0000-fb7a2c4b0e7f to complete...
✅ Task 10041707-1172-0358-0000-fb7a2c4b0e7f is ready!
📥 Retrieving results for task 10041707-1172-0358-0000-fb7a2c4b0e7f
✅ Retrieved 40 reviews

============================================================
✅ SUCCESS! Retrieved 40 reviews
============================================================
```

---

## Lambda Integration

### Handler Updates

**File**: `src/serpapi_collector/handler.py`

**Logic**:
```python
if source == 'trustpilot':
    # Use DataForSEO for Trustpilot
    dataforseo_creds = secrets_client.get_dataforseo_credentials()
    api_client = DataForSEOTrustpilotClient(
        login=dataforseo_creds['login'],
        password=dataforseo_creds['password']
    )
else:
    # Use SerpAPI for App Store and Google Play
    serpapi_key = secrets_client.get_serpapi_key()
    api_client = SerpAPIAppStoreClient(serpapi_key)  # або GooglePlay
```

### Invocation Example
```bash
aws lambda invoke \
  --function-name serpapi-collector-lambda \
  --payload '{
    "source": "trustpilot",
    "app_identifier": "www.zara.com",
    "brand": "zara",
    "limit": 40
  }' \
  response.json
```

---

## Cost Estimation

### DataForSEO Pricing

**Біллінг**: За кожні 20 відгуків (1 SERP)

| Запитано відгуків | Округлено до | SERPs | Приблизна вартість |
|-------------------|--------------|-------|-------------------|
| 1-20 | 20 | 1 | $0.00075 |
| 21-40 | 40 | 2 | $0.0015 |
| 41-60 | 60 | 3 | $0.00225 |
| 100 | 100 | 5 | $0.00375 |
| 1000 | 1000 | 50 | $0.0375 |

**Формула**: `cost = (depth / 20) × $0.00075`

**Приклад**: 45 відгуків
- Округлено до: 60 (кратне 20)
- SERPs: 60 / 20 = 3
- Вартість: 3 × $0.00075 = **$0.00225**

### Comparison with SerpAPI
- **SerpAPI**: $0.01 per search (max 20 reviews)
- **DataForSEO**: $0.00075 per SERP (20 reviews)
- **For 100 reviews**:
  - SerpAPI: 5 searches × $0.01 = **$0.05**
  - DataForSEO: 5 SERPs × $0.00075 = **$0.00375**
  
**Висновок**: DataForSEO дешевше у ~13 разів! 🎉

---

## Troubleshooting

### Problem: Task timeout
**Error**: `TimeoutError: Task did not complete within 60 seconds`

**Solution**:
- Збільшити `max_poll_attempts` в конфігурації
- Зменшити `depth` (кількість відгуків)
- Перевірити статус задачі вручну через API

### Problem: Authentication failed
**Error**: `401 Unauthorized`

**Solution**:
```bash
# Verify credentials
echo "mglushko@perfsys.com:cd0bdc42c24cad76" | base64

# Test auth
curl -X GET \
  "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/tasks_ready" \
  -H "Authorization: Basic bWdsdXNoa29AcGVyZnN5cy5jb206Y2QwYmRjNDJjMjRjYWQ3Ng=="
```

### Problem: Invalid domain
**Error**: `Domain not found on Trustpilot`

**Solution**:
- Перевірити формат domain: має бути повний домен (e.g., "www.zara.com")
- Перевірити чи існує business на Trustpilot: https://www.trustpilot.com/review/{domain}

---

## Export to CSV (Optional)

Якщо потрібен експорт у CSV формат:

```bash
# Get results as JSON
curl --location --request GET \
  "https://api.dataforseo.com/v3/business_data/trustpilot/reviews/task_get/{task_id}" \
  --header "Authorization: Basic bWdsdXNoa29AcGVyZnN5cy5jb206Y2QwYmRjNDJjMjRjYWQ3Ng==" \
  -o reviews.json

# Convert to CSV using jq
jq -r '
  .tasks[] | .result[] | .items[] | [
    (.title // ""),
    (.rating.value // ""),
    (.publication_date // ""),
    (.author.name // ""),
    (.review_text // "" | gsub("\n"; " "))
  ] | @csv
' reviews.json > reviews.csv
```

**CSV Headers**: title, rating, date, author, text

---

## Summary

### ✅ Переваги DataForSEO
- Більша кількість відгуків за запит (до 5000)
- Детальніша інформація про автора
- Стабільніші дані

### ⚠️ Недоліки
- Асинхронна модель (складніша)
- Довший час виконання (5-10 секунд)
- Потребує polling

### 🎯 Рекомендації
- Використовувати для Trustpilot (замість SerpAPI)
- Оптимальний `depth`: 40-100 відгуків
- Polling interval: 2-3 секунди
- Timeout: 60 секунд (20 спроб × 3 сек)

---

**Документація актуальна на**: 2024-10-04

