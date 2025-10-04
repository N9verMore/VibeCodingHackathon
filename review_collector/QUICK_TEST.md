# Quick Test Commands 🧪

Швидкі команди для тестування NewsAPI integration.

---

## 🔐 1. Setup Credentials

```bash
# Додати NewsAPI key в Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {"api_key": "YOUR_SERPAPI_KEY"},
    "dataforseo": {"login": "email", "password": "pass"},
    "newsapi": {"api_key": "YOUR_NEWSAPI_KEY"}
  }'

# Перевірити
aws secretsmanager get-secret-value \
  --secret-id review-collector/credentials | jq -r .SecretString | jq
```

---

## 🚀 2. Deploy

```bash
cd cdk
source .venv/bin/activate

# Показати зміни
cdk diff

# Deploy
cdk deploy

# Зберегти outputs
cdk deploy --outputs-file outputs.json
```

---

## 🧪 3. Test Endpoints

### Отримати API URL
```bash
# З outputs.json
export NEWS_API=$(jq -r '.ReviewCollectorStack.CollectNewsEndpoint' cdk/outputs.json)
echo $NEWS_API
```

### Базовий тест
```bash
curl -X POST "$NEWS_API" \
  -H "Content-Type: application/json" \
  -d '{"brand":"Tesla","limit":5}' | jq
```

### Тест з параметрами
```bash
curl -X POST "$NEWS_API" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Apple",
    "limit": 10,
    "search_type": "everything",
    "language": "en",
    "from_date": "2025-10-01"
  }' | jq
```

### Тест top-headlines
```bash
curl -X POST "$NEWS_API" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "technology",
    "limit": 5,
    "search_type": "top-headlines",
    "country": "us",
    "category": "technology"
  }' | jq
```

---

## 📊 4. Verify Database

### Count новин у DynamoDB
```bash
aws dynamodb scan \
  --table-name ReviewsTableV2 \
  --filter-expression "source = :news" \
  --expression-attribute-values '{":news":{"S":"news"}}' \
  --select COUNT
```

### Показати останні 5 новин
```bash
aws dynamodb scan \
  --table-name ReviewsTableV2 \
  --filter-expression "source = :news" \
  --expression-attribute-values '{":news":{"S":"news"}}' \
  --max-items 5 | jq '.Items[] | {id: .id.S, title: .title.S, source_name: .source_name.S}'
```

### Query по бренду
```bash
aws dynamodb query \
  --table-name ReviewsTableV2 \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand":{"S":"tesla"}}' \
  --scan-index-forward false \
  --max-items 5 | jq
```

---

## 🔍 5. Monitor Logs

### Real-time logs
```bash
aws logs tail /aws/lambda/news-collector-lambda --follow
```

### Останні помилки
```bash
aws logs tail /aws/lambda/news-collector-lambda --since 1h | grep ERROR
```

### Statistics
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/news-collector-lambda \
  --start-time $(date -u -d '1 hour ago' +%s)000 \
  --filter-pattern "Statistics" | jq -r '.events[].message'
```

---

## 🧹 6. Test Lambda Directly

### Invoke Lambda function
```bash
aws lambda invoke \
  --function-name news-collector-lambda \
  --payload '{"brand":"Tesla","limit":5}' \
  response.json

cat response.json | jq
```

### With all parameters
```bash
aws lambda invoke \
  --function-name news-collector-lambda \
  --payload '{
    "brand":"artificial intelligence",
    "limit":10,
    "search_type":"everything",
    "language":"en",
    "from_date":"2025-10-01"
  }' \
  response.json

cat response.json | jq
```

---

## 📈 7. Performance Test

### Sequential requests
```bash
for i in {1..5}; do
  echo "Request $i..."
  curl -s -X POST "$NEWS_API" \
    -H "Content-Type: application/json" \
    -d '{"brand":"tech","limit":5}' | jq -r '.statistics.duration_seconds'
  sleep 2
done
```

### Measure response time
```bash
time curl -X POST "$NEWS_API" \
  -H "Content-Type: application/json" \
  -d '{"brand":"Tesla","limit":50}'
```

---

## 🎯 8. Validation Tests

### Test error handling - missing brand
```bash
curl -X POST "$NEWS_API" \
  -H "Content-Type: application/json" \
  -d '{"limit":5}' | jq
# Expected: 400 ValidationError
```

### Test error handling - invalid limit
```bash
curl -X POST "$NEWS_API" \
  -H "Content-Type: application/json" \
  -d '{"brand":"test","limit":1000}' | jq
# Expected: 400 ValidationError
```

### Test error handling - invalid search_type
```bash
curl -X POST "$NEWS_API" \
  -H "Content-Type: application/json" \
  -d '{"brand":"test","search_type":"invalid"}' | jq
# Expected: 400 ValidationError
```

---

## 🔄 9. Compare with Reviews

### Check reviews still work
```bash
export REVIEW_API=$(jq -r '.ReviewCollectorStack.CollectReviewsEndpoint' cdk/outputs.json)

curl -X POST "$REVIEW_API" \
  -H "Content-Type: application/json" \
  -d '{
    "source":"appstore",
    "app_identifier":"544007664",
    "brand":"telegram",
    "limit":5
  }' | jq '.statistics'
```

### Count all data
```bash
# Reviews
aws dynamodb scan --table-name ReviewsTableV2 \
  --filter-expression "source IN (:as, :gp, :tp)" \
  --expression-attribute-values '{
    ":as":{"S":"appstore"},
    ":gp":{"S":"googleplay"},
    ":tp":{"S":"trustpilot"}
  }' --select COUNT

# News
aws dynamodb scan --table-name ReviewsTableV2 \
  --filter-expression "source = :news" \
  --expression-attribute-values '{":news":{"S":"news"}}' \
  --select COUNT
```

---

## 🧼 10. Cleanup (Optional)

### Delete test data
```bash
# CAUTION: This will delete ALL news items!
# aws dynamodb scan --table-name ReviewsTableV2 \
#   --filter-expression "source = :news" \
#   --expression-attribute-values '{":news":{"S":"news"}}' \
#   --projection-expression "pk" | \
#   jq -r '.Items[].pk.S' | \
#   xargs -I {} aws dynamodb delete-item \
#     --table-name ReviewsTableV2 \
#     --key '{"pk":{"S":"{}"}}'
```

### Destroy stack (full cleanup)
```bash
# CAUTION: This will delete everything!
# cdk destroy
```

---

## ✅ Success Checklist

- [ ] Credentials додані в Secrets Manager
- [ ] CDK stack успішно deployed
- [ ] Endpoint повертає 200 OK
- [ ] Новини зберігаються в DynamoDB
- [ ] Logs показують успішне виконання
- [ ] GSI query працює для news
- [ ] Review collection все ще працює
- [ ] Validation errors працюють коректно

---

## 📚 More Info

- **Full Guide**: [NEWSAPI_GUIDE.md](./NEWSAPI_GUIDE.md)
- **Examples**: `./examples/news_examples.sh`
- **Deployment**: [NEWS_DEPLOYMENT_SUMMARY.md](./NEWS_DEPLOYMENT_SUMMARY.md)

---

**Happy Testing! 🎉**

