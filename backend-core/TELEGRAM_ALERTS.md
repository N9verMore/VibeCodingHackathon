# 🚨 Telegram Alerts System - Документація

## Огляд

Автоматична система алертів через Telegram Bot при різкому збільшенні негативних згадок про бренд.

---

## 🔧 Налаштування

### 1. Створити Telegram Bot

1. Відкрити [@BotFather](https://t.me/BotFather) в Telegram
2. Відправити `/newbot`
3. Вказати ім'я бота
4. Отримати **BOT TOKEN** (схожий на `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Отримати Chat ID

**Варіант A: Через @userinfobot**
1. Відкрити [@userinfobot](https://t.me/userinfobot)
2. Натиснути Start
3. Скопіювати **ID** (це ваш chat_id)

**Варіант B: Через API**
1. Відправити повідомлення вашому боту
2. Відкрити: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Знайти `"chat":{"id":123456789}`

### 3. Додати в .env

```bash
# .env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

---

## 🎯 Як працює

### Автоматична перевірка

Після кожного додавання відгуків через `/api/reviews/external`:

1. **Аналіз останніх 2 днів** vs попередні 2 дні
2. **Порівняння негативу**: якщо збільшення ≥ 1.5x
3. **AI аналіз**: генерація summary про проблеми
4. **Telegram Alert**: автоматична відправка

### Формула детекції

```python
recent_negative / baseline_negative >= 1.5x
```

**Приклад:**
- Попередні 2 дні: 10 негативних відгуків
- Останні 2 дні: 16 негативних відгуків
- Ratio: 16/10 = 1.6x → **ALERT!** 🚨

---

## 📋 Формат алерту

### Telegram повідомлення:

```
🚨 ALERT: Збільшення негативних згадок

📱 Бренд: Zara
📊 Період: Останні 2 дні

Статистика:
• Всього згадувань: 45
• ❌ Негативні: 28
• ✅ Позитивні: 10
• 📈 Зростання негативу: 1.8x

🤖 AI Аналіз:
Виявлено різке зростання скарг на проблеми з оплатою. 
Користувачі повідомляють про краші додатку при checkout. 
Рекомендується термінова перевірка payment gateway.

⚠️ Топ проблеми:
1. оплата: 15 згадувань
2. краш: 8 згадувань
3. додаток: 5 згадувань

🔗 Перевірити деталі в dashboard
```

---

## 🔍 API Ендпоінти

### 1. Автоматична перевірка (при додаванні)

```bash
POST /api/reviews/external
```

Автоматично перевіряє алерти після додавання і відправляє в Telegram якщо потрібно.

### 2. Ручна перевірка всіх брендів

```bash
GET /api/alerts/check
```

**Response:**
```json
{
  "alert_detected": true,
  "alert": {
    "brand_name": "Zara",
    "negative_count": 28,
    "positive_count": 10,
    "total_mentions": 45,
    "increase_ratio": 1.8,
    "baseline_negative": 15,
    "ai_summary": "Виявлено різке зростання скарг...",
    "top_issues": [
      {"category": "оплата", "count": 15},
      {"category": "краш", "count": 8}
    ],
    "recommendations": [
      "Перевірити payment gateway",
      "Виправити краші при checkout"
    ]
  }
}
```

### 3. Перевірка конкретного бренду

```bash
GET /api/alerts/check?brand_name=Zara
```

---

## 🎨 Приклади використання

### Python:

```python
import requests

# Ручна перевірка
response = requests.get("http://localhost:8000/api/alerts/check").json()

if response["alert_detected"]:
    alert = response["alert"]
    print(f"🚨 ALERT for {alert['brand_name']}")
    print(f"Негативних: {alert['negative_count']} ({alert['increase_ratio']:.1f}x)")
    print(f"\nAI: {alert['ai_summary']}")
    print(f"\nТоп проблеми:")
    for issue in alert['top_issues']:
        print(f"  - {issue['category']}: {issue['count']}")
```

### cURL:

```bash
# Перевірка всіх брендів
curl http://localhost:8000/api/alerts/check

# Перевірка Zara
curl "http://localhost:8000/api/alerts/check?brand_name=Zara"
```

---

## ⚙️ Конфігурація

### config.py параметри:

```python
# Перевірка за останні N днів
ALERT_CHECK_DAYS = 2

# Мінімальне збільшення для алерту
ALERT_NEGATIVE_INCREASE_THRESHOLD = 1.5  # 1.5x
```

### Зміна порогу:

```python
# .env
ALERT_CHECK_DAYS=3
ALERT_NEGATIVE_INCREASE_THRESHOLD=2.0
```

---

## 🔥 Advanced: Manual Alert Send

```python
from app.telegram_service import telegram_service

# Кастомний алерт
custom_alert = {
    "brand_name": "Zara",
    "negative_count": 50,
    "positive_count": 5,
    "total_mentions": 60,
    "increase_ratio": 2.5,
    "ai_summary": "Критична ситуація!",
    "top_issues": [
        {"category": "payment", "count": 30},
        {"category": "crash", "count": 20}
    ]
}

telegram_service.send_alert(custom_alert)
```

---

## 📊 Dashboard Integration

### React приклад:

```jsx
function AlertMonitor() {
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    const checkAlerts = async () => {
      const response = await fetch('/api/alerts/check');
      const data = await response.json();
      
      if (data.alert_detected) {
        setAlert(data.alert);
      }
    };

    // Перевірка кожні 5 хвилин
    checkAlerts();
    const interval = setInterval(checkAlerts, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  if (!alert) return null;

  return (
    <div className="alert alert-danger">
      <h3>🚨 Alert: {alert.brand_name}</h3>
      <p>Збільшення негативу: {alert.increase_ratio}x</p>
      <p>{alert.ai_summary}</p>
      
      <h4>Топ проблеми:</h4>
      <ul>
        {alert.top_issues.map(issue => (
          <li key={issue.category}>
            {issue.category}: {issue.count} згадувань
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 🧪 Тестування

### 1. Тест відправки в Telegram

```python
import requests

# Додати багато негативних відгуків
negative_reviews = {
    "reviews": [
        {
            "id": f"test_{i}",
            "brand": "TestBrand",
            "source": "appstore",
            "text": "App crashes all the time!",
            "rating": 1,
            "created_at": "2025-10-05T10:00:00",
            "sentiment": "негативний",
            "description": "Crash issue",
            "categories": ["crash"],
            "severity": "critical"
        }
        for i in range(20)
    ],
    "count": 20
}

# Додаємо
response = requests.post(
    "http://localhost:8000/api/reviews/external",
    json=negative_reviews
)

# Якщо це збільшення - отримаєте Telegram alert!
```

### 2. Ручна перевірка

```bash
curl http://localhost:8000/api/alerts/check?brand_name=TestBrand
```

---

## ⚠️ Troubleshooting

### Alert не відправляється?

1. **Перевірте .env:**
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

2. **Перевірте бота:**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   ```

3. **Перевірте логи:**
   ```
   Telegram message sent successfully ✅
   або
   Failed to send Telegram message ❌
   ```

### Немає алертів?

- Перевірте чи є збільшення ≥ 1.5x
- Потрібні дані за попередні 2 дні для порівняння
- Логи: `Alert detected` або `No alerts detected`

---

## ✅ Summary

**Що реалізовано:**
- ✅ Автоматична перевірка при додаванні відгуків
- ✅ Telegram Bot інтеграція
- ✅ AI аналіз причин збільшення негативу
- ✅ Детальна статистика в алерті
- ✅ Топ проблемних категорій
- ✅ Ручна перевірка через API

**Endpoints:**
- `POST /api/reviews/external` - автоматична перевірка
- `GET /api/alerts/check` - ручна перевірка всіх
- `GET /api/alerts/check?brand_name=X` - перевірка бренду

**Configuration:**
```bash
# .env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
ALERT_CHECK_DAYS=2
ALERT_NEGATIVE_INCREASE_THRESHOLD=1.5
```

**Готово до використання!** 🚀
