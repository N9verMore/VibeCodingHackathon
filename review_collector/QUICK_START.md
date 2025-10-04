# ⚡ Review Collector API - Швидкий старт

## 🎯 Що це?

API для збору відгуків з App Store, Google Play та Trustpilot за одним запитом.

---

## 🚀 За 3 кроки

### 1️⃣ Знайдіть ID додатка

**App Store**: `https://apps.apple.com/us/app/telegram/id544007664` → `544007664`  
**Google Play**: `https://play.google.com/.../id=org.telegram.messenger` → `org.telegram.messenger`  
**Trustpilot**: `https://www.trustpilot.com/review/telegram.org` → `telegram.org`

### 2️⃣ Зробіть запит

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

### 3️⃣ Отримайте результат

```json
{
  "success": true,
  "statistics": {
    "fetched": 100,
    "saved": 95,
    "skipped": 5,
    "duration_seconds": 12.5
  }
}
```

---

## 📋 Мінімальні параметри

```json
{
  "source": "appstore | googleplay | trustpilot",
  "app_identifier": "ID додатка",
  "brand": "назва бренду"
}
```

---

## 💡 Приклади

### App Store (Telegram)
```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{"source":"appstore","app_identifier":"544007664","brand":"telegram","limit":50}'
```

### Google Play (WhatsApp)
```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{"source":"googleplay","app_identifier":"com.whatsapp","brand":"whatsapp","limit":50}'
```

### Trustpilot (Amazon)
```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{"source":"trustpilot","app_identifier":"amazon.com","brand":"amazon","limit":20}'
```

---

## 🔧 Python код

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

data = response.json()
if data['success']:
    print(f"✅ Зібрано {data['statistics']['saved']} нових відгуків")
else:
    print(f"❌ Помилка: {data['message']}")
```

---

## ⚡ Що далі?

📘 **Повна інструкція**: [API_INSTRUCTIONS.md](API_INSTRUCTIONS.md)  
📋 **Схема API**: [API_SCHEMA.md](API_SCHEMA.md)  
💡 **Більше прикладів**: [REQUEST_EXAMPLES.md](REQUEST_EXAMPLES.md)  

---

**Endpoint**: `https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews`  
**Статус**: ✅ Працює  
**Швидкість**: ~1-15 секунд на 100 відгуків

