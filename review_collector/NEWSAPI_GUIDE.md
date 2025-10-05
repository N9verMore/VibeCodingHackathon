# NewsAPI Integration Guide 🗞️

Повний гайд по інтеграції NewsAPI для збору новинних статей.

---

## 📋 Огляд

**NewsAPI Collector** - незалежний модуль для збору новин з [NewsAPI.org](https://newsapi.org).

### Особливості

✅ **Окрема Lambda** - незалежна від review collection  
✅ **Окремий endpoint** - `POST /collect-news`  
✅ **Та сама БД** - використовує `ReviewsTableV2`  
✅ **Два типи пошуку** - `/everything` та `/top-headlines`  
✅ **Автоматична пагінація** - збирає до 500 статей  
✅ **Ідемпотентність** - content-based deduplication  

---

## 🚀 Швидкий Старт

### 1. Отримати NewsAPI Key

```bash
# Реєстрація: https://newsapi.org/register
# Free tier: 100 requests/day
# Paid plans: від $449/міс
```

### 2. Додати API Key в Secrets Manager

```bash
# Оновити існуючий secret
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {"api_key": "YOUR_SERPAPI_KEY"},
    "dataforseo": {"login": "email", "password": "pass"},
    "newsapi": {"api_key": "YOUR_NEWSAPI_KEY"}
  }'
```

### 3. Deploy

```bash
cd cdk
cdk deploy
```

### 4. Збирати новини!

```bash
# Endpoint буде виведений після deploy
curl -X POST "https://YOUR_API_URL/collect-news" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Tesla",
    "limit": 50,
    "search_type": "everything"
  }'
```

---

## 📡 API Reference

### Endpoint

```
POST /collect-news
```

### Request Schema

```json
{
  "brand": "string",                    // Required - search term/keyword
  "limit": 100,                         // Optional - max articles (1-500), default: 100
  "search_type": "everything",          // Optional - "everything" or "top-headlines", default: "everything"
  
  // For "everything" search type:
  "from_date": "2025-10-01",           // Optional - start date (YYYY-MM-DD)
  "to_date": "2025-10-04",             // Optional - end date (YYYY-MM-DD)
  "language": "en",                    // Optional - language code (en, uk, ru, etc.)
  
  // For "top-headlines" search type:
  "country": "us",                     // Optional - country code (us, gb, ua, etc.)
  "category": "technology",            // Optional - business, entertainment, health, science, sports, technology
  "sources": "bbc-news,cnn"           // Optional - comma-separated source IDs
}
```

### Response

```json
{
  "success": true,
  "message": "News articles collected successfully",
  "statistics": {
    "brand": "Tesla",
    "search_type": "everything",
    "fetched": 100,
    "saved": 95,
    "skipped": 5,
    "errors": 0,
    "duration_seconds": 8.3,
    "start_time": "2025-10-04T14:30:00Z",
    "end_time": "2025-10-04T14:30:08.3Z"
  },
  "request": {
    "brand": "Tesla",
    "limit": 100,
    "search_type": "everything"
  }
}
```

---

## 📚 Приклади Використання

### 1. Пошук новин про компанію

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Tesla",
    "limit": 50,
    "search_type": "everything",
    "language": "en"
  }'
```

### 2. Новини за певний період

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Apple",
    "limit": 100,
    "search_type": "everything",
    "from_date": "2025-10-01",
    "to_date": "2025-10-04",
    "language": "en"
  }'
```

### 3. Топ-хедлайни по країні

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "technology",
    "limit": 50,
    "search_type": "top-headlines",
    "country": "us",
    "category": "technology"
  }'
```

### 4. Новини з конкретних джерел

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "tech news",
    "limit": 30,
    "search_type": "top-headlines",
    "sources": "bbc-news,cnn,techcrunch"
  }'
```

### 5. Python приклад

```python
import requests

response = requests.post(
    'https://YOUR_API_URL/collect-news',
    json={
        'brand': 'artificial intelligence',
        'limit': 100,
        'search_type': 'everything',
        'language': 'en',
        'from_date': '2025-10-01'
    }
)

data = response.json()
print(f"Fetched: {data['statistics']['fetched']}")
print(f"Saved: {data['statistics']['saved']}")
```

---

## 🗄️ Database Schema

NewsArticle записи зберігаються в `ReviewsTableV2` з наступною структурою:

```json
{
  "pk": "news#bbc-news-2025-10-04-tesla-announces-new",
  "id": "bbc-news-2025-10-04-tesla-announces-new",
  "source": "news",
  "source_id": "bbc-news",
  "source_name": "BBC News",
  "backlink": "https://www.bbc.com/news/...",
  "brand": "tesla",
  "app_identifier": "bbc-news",
  "title": "Tesla announces new battery technology",
  "text": "Tesla has unveiled significant updates...",
  "description": "Brief summary...",
  "content": "Full article content...",
  "rating": -1,
  "author_hint": "BBC Technology Team",
  "image_url": "https://...",
  "language": "en",
  "country": "us",
  "created_at": "2025-10-04T10:30:00Z",
  "fetched_at": "2025-10-04T14:25:00Z",
  "is_processed": false,
  "content_hash": "abc123..."
}
```

### Особливості:

- `pk` = `"news#" + article_id`
- `source` = `"news"` (константа для всіх новин)
- `rating` = `-1` (індикатор "not applicable")
- `brand` = пошуковий термін
- `app_identifier` = `source_id` (для сумісності зі схемою)

---

## 🔍 Запити до БД

### Query новини по бренду

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ReviewsTableV2')

response = table.query(
    IndexName='brand-created_at-index',
    KeyConditionExpression='brand = :brand AND begins_with(#src, :news)',
    ExpressionAttributeNames={'#src': 'source'},
    ExpressionAttributeValues={
        ':brand': 'tesla',
        ':news': 'news'
    },
    ScanIndexForward=False,  # Newest first
    Limit=50
)

articles = response['Items']
```

### Фільтрувати по джерелу

```python
response = table.scan(
    FilterExpression='source = :news AND source_id = :source_id',
    ExpressionAttributeValues={
        ':news': 'news',
        ':source_id': 'bbc-news'
    }
)
```

---

## 🎯 Use Cases

### 1. Media Monitoring 📰

Відслідковування згадок бренду в новинах:

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -d '{"brand":"YourCompany","limit":100,"search_type":"everything"}'
```

### 2. Competitor Analysis 🔍

Моніторинг новин про конкурентів:

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -d '{"brand":"CompetitorName","limit":200,"from_date":"2025-10-01"}'
```

### 3. Industry News Aggregation 📊

Збір новин по індустрії:

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -d '{"brand":"artificial intelligence","limit":500,"language":"en"}'
```

### 4. Real-time Alerts ⚡

Топ-хедлайни для швидкого реагування:

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -d '{"brand":"breaking","search_type":"top-headlines","country":"us","limit":20}'
```

---

## 📊 NewsAPI Endpoints Comparison

| Feature | `/everything` | `/top-headlines` |
|---------|---------------|------------------|
| **Search depth** | Last 5 years | Last 24 hours |
| **Total articles** | Millions | ~1000 |
| **Best for** | Historical research | Breaking news |
| **Date range** | ✅ Supported | ❌ Not supported |
| **Language filter** | ✅ Supported | ❌ Not supported |
| **Country filter** | ❌ Not supported | ✅ Supported |
| **Category filter** | ❌ Not supported | ✅ Supported |
| **Sources** | All sources | Top sources only |

---

## 💰 Pricing

### NewsAPI Plans

| Plan | Price | Requests/day | Requests/month |
|------|-------|--------------|----------------|
| **Developer** | Free | 100 | ~3,000 |
| **Business** | $449/mo | 25,000 | 750,000 |
| **Enterprise** | Custom | Unlimited | Unlimited |

### AWS Costs

| Component | Cost (monthly) |
|-----------|----------------|
| Lambda (news) | ~$0.50 |
| DynamoDB | Shared with reviews |
| API Gateway | ~$0.20 |
| **Total** | **~$0.70 + NewsAPI plan** |

---

## 🛠️ Development

### Local Testing

```bash
cd src/news_collector

# Set environment
export TABLE_NAME=ReviewsTableV2
export SECRET_NAME=review-collector/credentials

# Test handler
python -c "
from handler import lambda_handler
event = {'brand': 'Tesla', 'limit': 10, 'search_type': 'everything'}
result = lambda_handler(event, None)
print(result)
"
```

### Direct Lambda Invocation

```bash
aws lambda invoke \
  --function-name news-collector-lambda \
  --payload '{"brand":"Tesla","limit":50}' \
  response.json

cat response.json | jq
```

---

## 🐛 Troubleshooting

### Problem: "NewsAPI credentials not found"

**Solution:**
```bash
# Verify secret exists
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials | jq -r .SecretString
```

### Problem: "API rate limit exceeded"

**Solution:** NewsAPI free tier має ліміт 100 requests/day. Чекайте або апгрейдьте план.

### Problem: "No articles found"

**Solution:** Перевірте:
- Правильність пошукового терміну
- Дати (NewsAPI зберігає статті тільки 5 років)
- Мовні обмеження

### Problem: Lambda timeout

**Solution:** Зменшіть `limit` або збільшіть timeout в CDK до 300 секунд.

---

## 📝 Supported Languages

NewsAPI підтримує:

`ar`, `de`, `en`, `es`, `fr`, `he`, `it`, `nl`, `no`, `pt`, `ru`, `sv`, `ud`, `zh`

Приклад:

```bash
curl -X POST "https://YOUR_API_URL/collect-news" \
  -d '{"brand":"технології","limit":50,"language":"uk"}'
```

---

## 🔗 Resources

- [NewsAPI Documentation](https://newsapi.org/docs)
- [NewsAPI Sources](https://newsapi.org/sources)
- [NewsAPI Register](https://newsapi.org/register)

---

## 🎯 Next Steps

1. **Sentiment Analysis** - додати визначення тональності статей
2. **Entity Extraction** - витягувати компанії, персони, локації
3. **Categorization** - автоматична категоризація новин
4. **Notifications** - alerts при важливих новинах
5. **Dashboard** - візуалізація зібраних новин

---

**Built with ❤️ using NewsAPI, AWS Lambda, and Python 3.11**

