# 🚀 Швидкий старт - Збір відгуків

Проста інструкція для збору відгуків через API.

---

## 📍 API Endpoint

```
https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews
```

---

## 📱 App Store

### Формат запиту:
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "APP_ID",
    "brand": "BRAND_NAME",
    "limit": 100
  }'
```

### Приклади:

**Zara:**
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "appstore", "app_identifier": "547951480", "brand": "zara", "limit": 100}'
```

**Telegram:**
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "appstore", "app_identifier": "544007664", "brand": "telegram", "limit": 100}'
```

**Як знайти App ID:**
- URL додатку: `https://apps.apple.com/app/idXXXXXXXXX`
- App ID = `XXXXXXXXX` (числа після "id")

**⏱️ Час виконання:** ~2-10 секунд  
**📊 Результат:** До 100 відгуків за запит

---

## 🤖 Google Play

### Формат запиту:
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "googleplay",
    "app_identifier": "PACKAGE_NAME",
    "brand": "BRAND_NAME",
    "limit": 100
  }'
```

### Приклади:

**Zara:**
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "googleplay", "app_identifier": "com.inditex.zara", "brand": "zara", "limit": 100}'
```

**Telegram:**
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "googleplay", "app_identifier": "org.telegram.messenger", "brand": "telegram", "limit": 100}'
```

**Як знайти Package Name:**
- URL додатку: `https://play.google.com/store/apps/details?id=PACKAGE_NAME`
- Package Name = те, що після `id=`

**⏱️ Час виконання:** ~5-15 секунд  
**📊 Результат:** До 100 відгуків за запит (з пагінацією)

---

## ⭐ Trustpilot

### Формат запиту:
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "trustpilot",
    "app_identifier": "www.DOMAIN.com",
    "brand": "BRAND_NAME",
    "limit": 40
  }'
```

### Приклади:

**Zara:**
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "trustpilot", "app_identifier": "www.zara.com", "brand": "zara", "limit": 40}'
```

**Tesla:**
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "trustpilot", "app_identifier": "www.tesla.com", "brand": "tesla", "limit": 40}'
```

**Booking.com:**
```bash
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "trustpilot", "app_identifier": "www.booking.com", "brand": "booking", "limit": 40}'
```

**Як знайти Domain:**
- URL компанії на Trustpilot: `https://www.trustpilot.com/review/DOMAIN`
- Використовуйте повний домен: `www.DOMAIN.com`

**⏱️ Час виконання:** ~15-25 секунд (асинхронна обробка DataForSEO)  
**📊 Результат:** До 40-60 відгуків за запит  
**⚠️ Важливо:** Рекомендуємо limit ≤ 40 через timeout API Gateway (29 сек)

---

## 📄 Формат відповіді

### Успішна відповідь:
```json
{
  "success": true,
  "message": "Reviews collected successfully",
  "statistics": {
    "brand": "zara",
    "app_identifier": "547951480",
    "fetched": 100,
    "saved": 99,
    "skipped": 1,
    "errors": 0,
    "start_time": "2025-10-04T16:08:36.626388",
    "duration_seconds": 1.723889,
    "end_time": "2025-10-04T16:08:38.350277"
  },
  "request": {
    "source": "appstore",
    "app_identifier": "547951480",
    "brand": "zara",
    "limit": 100,
    "country": "us",
    "metadata": {}
  }
}
```

### Помилка:
```json
{
  "success": false,
  "message": "Error description",
  "error": "ErrorType"
}
```

---

## 🎯 Параметри запиту

| Параметр | Тип | Обов'язковий | Опис |
|----------|-----|--------------|------|
| `source` | string | ✅ | Джерело: `appstore`, `googleplay`, `trustpilot` |
| `app_identifier` | string | ✅ | App ID / Package Name / Domain |
| `brand` | string | ✅ | Назва бренду для групування |
| `limit` | integer | ❌ | Кількість відгуків (default: 100) |

---

## 📊 Статистика відповіді

| Поле | Опис |
|------|------|
| `fetched` | Скільки відгуків отримано з API |
| `saved` | Скільки нових відгуків збережено в БД |
| `skipped` | Скільки відгуків пропущено (дублікати) |
| `errors` | Кількість помилок при обробці |
| `duration_seconds` | Час виконання запиту |

---

## 💾 Де зберігаються дані?

**DynamoDB Table:** `ReviewsTableV2`  
**Region:** `us-east-1`

### Перегляд даних:

**AWS CLI:**
```bash
aws dynamodb query \
  --table-name ReviewsTableV2 \
  --index-name brand-created_at-index \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand":{"S":"zara"}}' \
  --limit 10 \
  --profile hackathon
```

---

## ⚡ Швидкі команди

### Зібрати Zara з усіх джерел:
```bash
# App Store
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "appstore", "app_identifier": "547951480", "brand": "zara", "limit": 100}'

# Google Play
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "googleplay", "app_identifier": "com.inditex.zara", "brand": "zara", "limit": 100}'

# Trustpilot
curl -X POST "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{"source": "trustpilot", "app_identifier": "www.zara.com", "brand": "zara", "limit": 40}'
```

---

## 🔧 Troubleshooting

### Помилка: "Invalid API key"
- Перевірте, чи правильний SerpAPI ключ у Secrets Manager

### Помилка: "DataForSEO login and password are required"
- Додайте DataForSEO credentials в Secrets Manager

### Помилка: "Endpoint request timed out"
- Для Trustpilot: зменшіть `limit` до 40 або менше
- API Gateway має timeout 29 секунд

### Повільна відповідь на Trustpilot
- Це нормально - DataForSEO використовує асинхронну обробку
- Очікуваний час: 15-25 секунд

---

## 📚 Додаткова документація

- **Повний гайд:** `SERPAPI_GUIDE.md`
- **Виправлення дат:** `DATE_ISSUE_FIX_SUMMARY.md`
- **Deployment:** `DEPLOYMENT.md`
- **База даних:** `DATABASE_ACCESS.md`

---

**Створено:** 2025-10-04  
**API Version:** 1.0  
**Статус:** ✅ Production Ready

