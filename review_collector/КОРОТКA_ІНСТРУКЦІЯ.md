# Review Collector API - Коротка інструкція

## 🎯 Endpoint
```
POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews
```

---

## 📋 Формат запиту

```json
{
  "source": "appstore | googleplay | trustpilot",
  "app_identifier": "ID додатка",
  "brand": "назва бренду",
  "limit": 100
}
```

---

## 🔍 Як знайти ID додатка?

### App Store
URL: `https://apps.apple.com/us/app/telegram/id544007664`  
**ID**: `544007664` (цифри після `id`)

### Google Play
URL: `https://play.google.com/store/apps/details?id=org.telegram.messenger`  
**ID**: `org.telegram.messenger` (значення параметра `id`)

### Trustpilot
URL: `https://www.trustpilot.com/review/telegram.org`  
**ID**: `telegram.org` (домен після `/review/`)

---

## 💻 Приклад запиту

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100
  }'
```

---

## ✅ Відповідь

```json
{
  "success": true,
  "statistics": {
    "fetched": 100,    // Отримано
    "saved": 95,       // Збережено нових
    "skipped": 5,      // Дублікатів
    "errors": 0        // Помилок
  }
}
```

---

## ⚡ Python

```python
import requests

response = requests.post(
    'https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews',
    json={
        'source': 'appstore',
        'app_identifier': '544007664',
        'brand': 'telegram',
        'limit': 100
    }
)
print(response.json())
```

---

## 📊 Ліміти

| Платформа | Макс відгуків | Час |
|-----------|---------------|-----|
| App Store | 200+ | 1-15 сек |
| Google Play | 200+ | 1-15 сек |
| Trustpilot | 20 | 1-3 сек |

---

## ❌ Помилки

**Невірний source**:
```json
{"success": false, "error": "ValidationError", "message": "Invalid source..."}
```

**Відсутній параметр**:
```json
{"success": false, "error": "ValidationError", "message": "Missing required field..."}
```

---

**Детальна документація**: [API_INSTRUCTIONS.md](API_INSTRUCTIONS.md)

