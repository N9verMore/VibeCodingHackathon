# NewsAPI → NewsArticle Mapping 🗺️

Детальна схема маппінгу даних з NewsAPI в нашу структуру DynamoDB.

---

## 📥 NewsAPI Response Format

### Приклад відповіді від NewsAPI:

```json
{
  "status": "ok",
  "totalResults": 12345,
  "articles": [
    {
      "source": {
        "id": "bbc-news",
        "name": "BBC News"
      },
      "author": "Technology Correspondent",
      "title": "Tesla announces breakthrough in battery technology",
      "description": "Electric car maker Tesla has unveiled a new battery...",
      "url": "https://www.bbc.com/news/technology-12345678",
      "urlToImage": "https://ichef.bbci.co.uk/news/1024/image.jpg",
      "publishedAt": "2025-10-04T10:30:00Z",
      "content": "Tesla Inc has announced a major breakthrough in battery technology that could revolutionize the electric vehicle industry. The new batteries... [+2000 chars]"
    }
  ]
}
```

---

## 🔄 Mapping Process

### NewsAPI Article → NewsArticle Entity → DynamoDB Item

```
NewsAPI Field              NewsArticle Field       DynamoDB Field         Notes
─────────────────────────  ──────────────────────  ─────────────────────  ──────────────────────
source.id                  source_id               source_id              "bbc-news"
source.id                  app_identifier          app_identifier         Для сумісності зі схемою
source.name                source_name             source_name            "BBC News"
[generated]                id                      id                     bbc-news-2025-10-04-tesla-announces
[generated]                -                       pk                     news#bbc-news-2025-10-04-tesla-announces
[constant: "news"]         -                       source                 Завжди "news"

url                        url                     backlink               Оригінальне URL
[user input]               brand                   brand                  Пошуковий термін
title                      title                   title                  Заголовок статті
description                description             description            Короткий опис
content                    content                 content                Повний текст
description + content      -                       text                   Об'єднаний текст

author                     author                  author_hint            Автор статті
urlToImage                 image_url               image_url              URL зображення
[detected/default]         language                language               Мова статті (default: "en")
[user input]               country                 country                Країна з запиту

publishedAt                published_at            created_at             Дата публікації
[current time]             fetched_at              fetched_at             Час збору
[constant: false]          is_processed            is_processed           Чи оброблено
[computed SHA256]          content_hash            content_hash           Hash для ідемпотентності

[constant: -1]             -                       rating                 -1 = не застосовується
```

---

## 🆔 ID Generation Logic

ID генерується для унікальної ідентифікації статті:

```python
# Формат
article_id = f"{source_id}-{date}-{title_snippet}"

# Приклад
source_id = "bbc-news"
date = "2025-10-04"  # з publishedAt
title_snippet = "tesla-announces-breakthrough"[:30]  # перші 30 символів

article_id = "bbc-news-2025-10-04-tesla-announces-breakthrough"
```

### Правила очищення ID:
- Пробіли → `-`
- Slash `/` → `-`
- Тільки alphanumeric + `-_`
- Lowercase

---

## 📊 Приклад Повного Маппінгу

### NewsAPI Response:

```json
{
  "source": {
    "id": "techcrunch",
    "name": "TechCrunch"
  },
  "author": "Sarah Johnson",
  "title": "Apple unveils new AI features for iPhone 16",
  "description": "Apple has announced groundbreaking AI capabilities...",
  "url": "https://techcrunch.com/2025/10/04/apple-ai-iphone-16/",
  "urlToImage": "https://techcrunch.com/wp-content/uploads/2025/10/apple-ai.jpg",
  "publishedAt": "2025-10-04T14:30:00Z",
  "content": "In a surprise announcement today, Apple revealed new artificial intelligence features coming to the iPhone 16. The features include..."
}
```

### Після маппінгу → DynamoDB Item:

```json
{
  "pk": "news#techcrunch-2025-10-04-apple-unveils-new-ai-featu",
  "id": "techcrunch-2025-10-04-apple-unveils-new-ai-featu",
  "source": "news",
  "source_id": "techcrunch",
  "source_name": "TechCrunch",
  "backlink": "https://techcrunch.com/2025/10/04/apple-ai-iphone-16/",
  "brand": "apple",
  "app_identifier": "techcrunch",
  "title": "Apple unveils new AI features for iPhone 16",
  "text": "Apple has announced groundbreaking AI capabilities...\n\nIn a surprise announcement today, Apple revealed new artificial intelligence features coming to the iPhone 16. The features include...",
  "description": "Apple has announced groundbreaking AI capabilities...",
  "content": "In a surprise announcement today, Apple revealed new artificial intelligence features coming to the iPhone 16. The features include...",
  "rating": -1,
  "author_hint": "Sarah Johnson",
  "image_url": "https://techcrunch.com/wp-content/uploads/2025/10/apple-ai.jpg",
  "language": "en",
  "country": "us",
  "created_at": "2025-10-04T14:30:00Z",
  "fetched_at": "2025-10-04T15:00:00Z",
  "is_processed": false,
  "content_hash": "a1b2c3d4e5f6..."
}
```

---

## 🔑 Ключові Особливості

### 1. Primary Key (pk)
```
Format: news#{article_id}
Example: news#bbc-news-2025-10-04-tesla-announces-breakthrough
```

Це забезпечує:
- ✅ Унікальність в таблиці
- ✅ Розділення з reviews (які мають формат `appstore#id`)
- ✅ Простий пошук за ID

### 2. Source Field
```
Завжди: "news"
```

Це дозволяє:
- ✅ Фільтрувати всі новини: `source = 'news'`
- ✅ Відрізняти від reviews: `source IN ('appstore', 'googleplay', 'trustpilot')`
- ✅ Використовувати GSI `brand-created_at-index`

### 3. Rating Field
```
Завжди: -1
```

Чому -1, а не 0 або NULL?
- ✅ `-1` = "not applicable" (семантично ясно)
- ✅ Відрізняється від reviews (1-5)
- ✅ Можна використати в майбутньому для sentiment score

### 4. Text Field
```
Format: {description}\n\n{content}
```

Об'єднуємо description + content для:
- ✅ Сумісності з Review schema
- ✅ Повнотекстового пошуку
- ✅ Збереження повної інформації

---

## 🎨 Field Types

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| id | string | ✅ | - | Non-empty |
| source_id | string | ✅ | - | Non-empty |
| source_name | string | ✅ | - | - |
| url | string | ✅ | - | Valid URL |
| brand | string | ✅ | - | Search term |
| title | string | ✅ | - | Non-empty |
| description | string | ❌ | null | - |
| content | string | ❌ | null | - |
| author | string | ❌ | null | - |
| image_url | string | ❌ | null | Valid URL |
| language | string | ✅ | "en" | ISO code |
| country | string | ❌ | null | ISO code |
| published_at | datetime | ✅ | - | ISO 8601 |
| fetched_at | datetime | ✅ | now() | ISO 8601 |
| is_processed | boolean | ✅ | false | - |
| content_hash | string | ✅ | computed | SHA256 |

---

## 🔍 Query Examples

### 1. Отримати всі новини

```python
response = table.scan(
    FilterExpression='source = :news',
    ExpressionAttributeValues={':news': 'news'}
)
```

### 2. Новини по бренду (використовуючи GSI)

```python
response = table.query(
    IndexName='brand-created_at-index',
    KeyConditionExpression='brand = :brand',
    FilterExpression='source = :news',
    ExpressionAttributeValues={
        ':brand': 'tesla',
        ':news': 'news'
    },
    ScanIndexForward=False  # Newest first
)
```

### 3. Новини з певного джерела

```python
response = table.scan(
    FilterExpression='source = :news AND source_id = :source_id',
    ExpressionAttributeValues={
        ':news': 'news',
        ':source_id': 'bbc-news'
    }
)
```

### 4. Непроцесовані новини

```python
response = table.scan(
    FilterExpression='source = :news AND is_processed = :false',
    ExpressionAttributeValues={
        ':news': 'news',
        ':false': False
    }
)
```

---

## 🧮 Content Hash Calculation

Hash обчислюється для ідемпотентності:

```python
stable_fields = [
    article.id,
    article.source_id,
    article.source_name,
    article.url,
    article.brand,
    article.title,
    article.description or "",
    article.content or "",
    article.author or "",
    article.language,
    article.country or "",
    article.published_at.isoformat(),
]

content = "|".join(stable_fields)
content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
```

**Поля, що НЕ входять в hash:**
- `fetched_at` - змінюється при кожному збору
- `is_processed` - змінюється при обробці

---

## 📝 Usage in Code

### Створення NewsArticle:

```python
from news_article import NewsArticle
from datetime import datetime

article = NewsArticle(
    id="bbc-news-2025-10-04-tesla",
    source_id="bbc-news",
    source_name="BBC News",
    url="https://www.bbc.com/news/...",
    brand="tesla",
    title="Tesla announces...",
    description="Short description",
    content="Full content",
    author="Author Name",
    image_url="https://...",
    language="en",
    country="us",
    published_at=datetime(2025, 10, 4, 10, 30),
    fetched_at=datetime.utcnow()
)

# Автоматично генерується content_hash
print(article.content_hash)

# Конвертація в DynamoDB
item = article.to_dynamodb_item()
```

### Збереження в DynamoDB:

```python
from news_repository import NewsArticleRepository

repo = NewsArticleRepository()
was_saved = repo.save(article)  # True if new/updated, False if duplicate
```

---

## ✨ Future Enhancements

### Можливі покращення:

1. **Sentiment Analysis**
   ```python
   # rating може використовуватись для sentiment score
   rating: -1 (not analyzed)
   rating: 1-2 (negative)
   rating: 3 (neutral)
   rating: 4-5 (positive)
   ```

2. **Language Detection**
   ```python
   from langdetect import detect
   article.language = detect(article.text)
   ```

3. **Entity Extraction**
   ```python
   # Додаткові поля
   entities: ["Tesla", "Elon Musk", "California"]
   categories: ["technology", "automotive", "business"]
   ```

4. **Image Processing**
   ```python
   # Зберігання зображення в S3
   image_s3_key: "news-images/bbc-news-2025-10-04.jpg"
   ```

---

**Готово до використання!** 🎉

