# NewsAPI Integration - Deployment Summary 🚀

## ✅ Що створено

### 1. Новий модуль `news_collector/`
```
src/news_collector/
├── handler.py                  # Lambda entry point
├── newsapi_client.py          # NewsAPI integration
├── news_article.py            # Domain entity (незалежна від Review)
├── news_repository.py         # DynamoDB adapter
├── collect_news_use_case.py   # Business logic
├── request_schema.py          # Validation
└── requirements.txt           # Dependencies
```

### 2. Оновлено інфраструктуру
- ✅ CDK Stack - додано `news-collector-lambda`
- ✅ API Gateway - новий endpoint `/collect-news`
- ✅ Secrets Client - підтримка NewsAPI key
- ✅ DynamoDB - використовує існуючу `ReviewsTableV2`

### 3. Документація
- ✅ `NEWSAPI_GUIDE.md` - повний гайд
- ✅ `examples/news_examples.sh` - curl приклади
- ✅ Оновлено головний `README.md`

---

## 🚀 Deployment Steps

### 1. Отримати NewsAPI Key

Зареєструватись на [newsapi.org/register](https://newsapi.org/register)

**Free tier**: 100 requests/day

### 2. Додати credentials в Secrets Manager

```bash
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {"api_key": "YOUR_SERPAPI_KEY"},
    "dataforseo": {"login": "email", "password": "pass"},
    "newsapi": {"api_key": "YOUR_NEWSAPI_KEY"}
  }'
```

### 3. Deploy CDK Stack

```bash
cd cdk
source .venv/bin/activate

# Preview changes
cdk diff

# Deploy
cdk deploy
```

### 4. Отримати endpoint URL

Після деплою ви побачите:
```
Outputs:
ReviewCollectorStack.CollectNewsEndpoint = https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/collect-news
ReviewCollectorStack.NewsLambdaFunctionName = news-collector-lambda
```

### 5. Тестувати

```bash
# Базовий запит
curl -X POST "https://YOUR_API_URL/collect-news" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Tesla",
    "limit": 10,
    "search_type": "everything"
  }'
```

---

## 📊 Database Schema

### NewsArticle в DynamoDB

```json
{
  "pk": "news#bbc-news-2025-10-04-tesla",
  "id": "bbc-news-2025-10-04-tesla",
  "source": "news",                    // Константа для всіх новин
  "source_id": "bbc-news",             // ID джерела
  "source_name": "BBC News",           // Назва джерела
  "backlink": "https://...",           // URL статті
  "brand": "tesla",                    // Пошуковий термін
  "app_identifier": "bbc-news",        // = source_id (для сумісності)
  "title": "Tesla announces...",
  "text": "Combined description + content",
  "description": "Short description",
  "content": "Full content",
  "rating": -1,                        // -1 = не застосовується
  "author_hint": "Author name",
  "image_url": "https://...",
  "language": "en",
  "country": "us",
  "created_at": "2025-10-04T10:00:00Z",
  "fetched_at": "2025-10-04T14:00:00Z",
  "is_processed": false,
  "content_hash": "sha256..."
}
```

### Ключові відмінності від Review:
- `pk` починається з `"news#"`
- `source` = `"news"` (константа)
- `rating` = `-1` (індикатор "not applicable")
- Додаткові поля: `source_id`, `source_name`, `description`, `content`, `image_url`

---

## 🔍 Query Patterns

### 1. Отримати новини по бренду

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ReviewsTableV2')

response = table.query(
    IndexName='brand-created_at-index',
    KeyConditionExpression='brand = :brand',
    FilterExpression='source = :news',
    ExpressionAttributeValues={
        ':brand': 'tesla',
        ':news': 'news'
    },
    ScanIndexForward=False,  # Newest first
    Limit=50
)
```

### 2. Отримати всі новини

```python
response = table.scan(
    FilterExpression='source = :news',
    ExpressionAttributeValues={':news': 'news'}
)
```

### 3. Фільтрувати по джерелу

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

## 🎯 API Examples

### 1. Пошук новин про компанію

```bash
curl -X POST "$API_URL/collect-news" \
  -d '{"brand":"Tesla","limit":50,"search_type":"everything","language":"en"}'
```

### 2. Новини за період

```bash
curl -X POST "$API_URL/collect-news" \
  -d '{
    "brand":"Apple",
    "limit":100,
    "search_type":"everything",
    "from_date":"2025-10-01",
    "to_date":"2025-10-04"
  }'
```

### 3. Топ-хедлайни

```bash
curl -X POST "$API_URL/collect-news" \
  -d '{
    "brand":"technology",
    "limit":20,
    "search_type":"top-headlines",
    "country":"us",
    "category":"technology"
  }'
```

---

## 💡 Tips

### Оптимізація витрат
- Free tier: 100 requests/day
- Використовуйте `limit` обережно (100 статей = 1-2 requests)
- Кешуйте результати

### Найкращі практики
- Використовуйте `from_date` для інкрементального збору
- `search_type="top-headlines"` для свіжих новин
- `search_type="everything"` для historical research

### Моніторинг
```bash
# CloudWatch logs
aws logs tail /aws/lambda/news-collector-lambda --follow

# Check DynamoDB
aws dynamodb scan --table-name ReviewsTableV2 \
  --filter-expression "source = :news" \
  --expression-attribute-values '{":news":{"S":"news"}}' \
  --select COUNT
```

---

## 🐛 Troubleshooting

### Problem: "NewsAPI credentials not found"

```bash
# Перевірте secret
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials
```

### Problem: Lambda timeout

```bash
# Збільшіть timeout у CDK stack
timeout=Duration.seconds(300)

cdk deploy
```

### Problem: Rate limit exceeded

Зменшіть `limit` або зачекайте (free tier обмеження).

---

## 📚 Resources

- **Документація**: [NEWSAPI_GUIDE.md](./NEWSAPI_GUIDE.md)
- **NewsAPI Docs**: https://newsapi.org/docs
- **Приклади**: [examples/news_examples.sh](./examples/news_examples.sh)

---

## ✨ Next Steps

1. **Deploy** інфраструктуру
2. **Test** endpoint з різними queries
3. **Monitor** CloudWatch logs
4. **Analyze** зібрані дані в DynamoDB

**Готово до використання!** 🎉

