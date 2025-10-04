# 🔧 Виправлення проблеми з датами - Підсумок

## 📊 Проблема

**Аномалія**: У базі даних виявлено 10x більше записів з датою "сьогодні" порівняно з іншими днями.

## 🔍 Причина

Знайдено **критичний баг** у всіх клієнтах для збору відгуків:

### ❌ Старий код (НЕПРАВИЛЬНО):
```python
try:
    if date_str:
        created_at = datetime.strptime(date_str, "%B %d, %Y")  # Невірний формат!
    else:
        created_at = datetime.utcnow()  # ⚠️ Встановлює СЬОГОДНІШНЮ дату!
except (ValueError, AttributeError) as e:
    logger.warning(f"Could not parse date '{date_str}': {e}")
    created_at = datetime.utcnow()  # ⚠️ Встановлює СЬОГОДНІШНЮ дату!
```

**Що відбувалося:**
1. ❌ Формат дати не співпадав: API повертає `"Aug 24, 2025"`, код очікував `"August 24, 2025"`
2. ❌ Парсинг не вдавався → встановлювалася **сьогоднішня дата**
3. ❌ Всі відгуки з невалідними датами отримували `created_at = datetime.utcnow()`
4. ❌ Це створювало штучний спайк на поточну дату

---

## ✅ Рішення

### 1. App Store (`serpapi_appstore_client.py`)

**Виявлені проблеми:**
- Поле: `review_date`
- Формат з API: `"Aug 24, 2025"` (скорочена назва місяця)
- Очікувався: `"October 1, 2024"` (повна назва місяця)

**Виправлення:**
```python
# Parse date
try:
    # SerpAPI Apple Reviews date formats:
    # - "Aug 24, 2025" (abbreviated month)
    # - "October 1, 2024" (full month)
    # - "2024-10-01" (ISO format)
    if date_str:
        if '-' in date_str:
            # ISO format: "2024-10-01"
            created_at = datetime.fromisoformat(date_str)
        else:
            # Try abbreviated month format first: "Aug 24, 2025"
            try:
                created_at = datetime.strptime(date_str, "%b %d, %Y")
            except ValueError:
                # Fall back to full month format: "October 1, 2024"
                created_at = datetime.strptime(date_str, "%B %d, %Y")
    else:
        logger.warning(f"Empty date string for review, skipping")
        raise ValueError("Empty date string")
except (ValueError, AttributeError) as e:
    logger.error(f"Could not parse date '{date_str}': {e}. Review will be skipped.")
    raise ValueError(f"Invalid date format: {date_str}")
```

**Ключові зміни:**
- ✅ Підтримка скороченої назви місяця (`%b` для "Aug")
- ✅ Fallback на повну назву місяця (`%B` для "August")
- ✅ **Пропуск відгуків з невалідними датами** замість встановлення сьогоднішньої дати
- ✅ Raise exception → відгук не зберігається

---

### 2. Google Play (`serpapi_googleplay_client.py`)

**Виявлені проблеми:**
- Поле 1: `date` = `"September 10, 2025"` (людино-читабельний формат)
- Поле 2: `iso_date` = `"2025-09-10T15:58:52Z"` (точний timestamp) ✅ **КРАЩИЙ ВАРІАНТ**
- Код використовував тільки `date`, ігноруючи `iso_date`
- Відсутній параметр `all_reviews=true` → пагінація не працювала (тільки 20 записів)

**Виправлення:**
```python
# Use iso_date (precise timestamp) if available, fallback to date (human readable)
date_str = raw_data.get('iso_date', '') or raw_data.get('date', '')

# Use SerpAPI provided ID if available
review_id = raw_data.get('id')  # Тепер використовуємо UUID з API!

# Parse date
try:
    # SerpAPI Google Play date formats:
    # - "2025-09-10T15:58:52Z" (iso_date - preferred)
    # - "September 10, 2025" (date - human readable)
    # - "2024-10-01" (ISO format)
    if date_str:
        # Remove 'Z' suffix if present (UTC timezone indicator)
        date_clean = date_str.rstrip('Z')
        
        if 'T' in date_clean:
            # ISO 8601 format: "2025-09-10T15:58:52"
            created_at = datetime.fromisoformat(date_clean)
        elif '-' in date_clean:
            # ISO date format: "2024-10-01"
            created_at = datetime.fromisoformat(date_clean)
        else:
            # Human readable format: "September 10, 2025"
            created_at = datetime.strptime(date_clean, "%B %d, %Y")
    else:
        logger.warning(f"Empty date string for review, skipping")
        raise ValueError("Empty date string")
except (ValueError, AttributeError) as e:
    logger.error(f"Could not parse date '{date_str}': {e}. Review will be skipped.")
    raise ValueError(f"Invalid date format: {date_str}")
```

**Виправлення пагінації:**
```python
params = {
    'engine': 'google_play_product',
    'product_id': app_identifier,
    'store': 'apps',
    'all_reviews': 'true',  # ✅ Додано! Тепер пагінація працює
    'sort_by': '2',  # 2 = newest
}
```

**Ключові зміни:**
- ✅ Пріоритет на `iso_date` (точний timestamp з мілісекундами)
- ✅ Підтримка ISO 8601 формату (`2025-09-10T15:58:52Z`)
- ✅ Використання UUID з API як `review_id`
- ✅ Додано `all_reviews=true` для пагінації
- ✅ **Пропуск відгуків з невалідними датами**

---

## 📈 Результати тестування

### ✅ Успішні запити після виправлення:

```bash
# App Store - Zara (100 відгуків)
curl -X POST "${API_URL}/collect-reviews" \
  -d '{"source": "appstore", "app_identifier": "547951480", "brand": "zara", "limit": 100}'

# Результат:
# ✅ fetched: 100, saved: 100, skipped: 0, errors: 0, duration: 9.09s
```

```bash
# Google Play - Zara (100 відгуків)  
curl -X POST "${API_URL}/collect-reviews" \
  -d '{"source": "googleplay", "app_identifier": "com.inditex.zara", "brand": "zara", "limit": 100}'

# Результат:
# ✅ fetched: 100, saved: 20, skipped: 80 (дублікати), errors: 0, duration: 4.64s
```

---

## 🔑 Інші зміни

### Оновлення SerpAPI ключа

```bash
aws secretsmanager put-secret-value \
  --region us-east-1 \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {"api_key": "48d2069ef25d9216d7b590b88b547e6050f3e06af26b1f11e6c3fdda17922639"},
    "dataforseo": {"login": "", "password": ""}
  }' \
  --profile hackathon
```

---

## 🎯 Висновки

### Що було виправлено:

1. ✅ **Формат дат App Store**: Підтримка скорочених назв місяців (`Aug` замість `August`)
2. ✅ **Формат дат Google Play**: Використання `iso_date` з точним timestamp
3. ✅ **Пагінація Google Play**: Додано `all_reviews=true` → тепер збирається >20 відгуків
4. ✅ **Обробка помилок**: Відгуки з невалідними датами тепер **пропускаються** замість встановлення `datetime.utcnow()`
5. ✅ **UUID з API**: Google Play тепер використовує реальні ID з API

### Що це означає:

- ❌ **Більше немає штучних спайків** на сьогоднішню дату
- ✅ Всі відгуки мають **правильні дати** з оригінальних платформ
- ✅ Відгуки з невалідними датами **не зберігаються** (замість неправильних даних)
- ✅ Google Play тепер збирає **100+ відгуків** (раніше тільки 20)

---

## 📝 Рекомендації

### Для очистки існуючих даних:

```python
# Скрипт для видалення відгуків з датою = сьогодні (можливо помилкові)
import boto3
from datetime import datetime, date

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('ReviewsTable')

today = date.today().isoformat()

# Знайти всі відгуки з датою = сьогодні
response = table.scan(
    FilterExpression='begins_with(created_at, :today)',
    ExpressionAttributeValues={':today': today}
)

suspicious_reviews = response['Items']
print(f"Знайдено {len(suspicious_reviews)} відгуків з датою = {today}")

# ВАЖЛИВО: Перевірити вручну перед видаленням!
# for item in suspicious_reviews:
#     table.delete_item(Key={'pk': item['pk']})
```

### Для моніторингу:

```sql
-- Запит для перевірки розподілу дат (в Athena/QuickSight)
SELECT 
    DATE(created_at) as review_date,
    COUNT(*) as count,
    source
FROM reviews_table
GROUP BY DATE(created_at), source
ORDER BY review_date DESC
LIMIT 30;
```

---

**Автор:** AI Assistant  
**Дата:** 2025-10-04  
**Статус:** ✅ Виправлено і протестовано

