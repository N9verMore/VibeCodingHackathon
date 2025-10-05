# BrandPulse - Brand Reputation Monitoring System

🚀 **VibeCodingHackathon Project**

Система моніторингу репутації бренду з AI-аналізом, детекцією криз та автоматичною генерацією відповідей.

## 🎯 Killer Features

1. **Live Crisis Detection** - автоматичне виявлення сплесків негативних відгуків
2. **AI Response Co-pilot** - генерація персоналізованих відповідей у різних стилях
3. **Reputation Health Score** - інтегральна оцінка репутації (0-100)
4. **Smart Chat** - запитуйте про бренд у вільній формі

## 📦 Швидкий старт

### 1. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 2. Налаштування

Створіть файл `.env`:
```bash
cp .env.example .env
```

Додайте ваш OpenAI API key у `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Генерація тестових даних

```bash
python scripts/generate_test_data.py
```

### 4. Запуск сервера

```bash
python app/main.py
```

API буде доступний на `http://localhost:8000`

## 📡 API Endpoints

### Додавання даних

**Додати коментар/відгук:**
```bash
POST /api/comments
{
  "body": "Додаток постійно вилітає!",
  "timestamp": "2025-10-04T14:30:00",
  "rating": 1.0,
  "platform": "app_store",
  "sentiment": "negative",
  "category": "payment_crash"
}
```

**Додати документ (база знань):**
```bash
POST /api/documents
{
  "title": "FAQ про доставку",
  "content": "Інформація про доставку...",
  "doc_type": "faq"
}
```

**Додати результат Google SERP:**
```bash
POST /api/serp
{
  "query": "Zara reviews",
  "title": "Відгуки про Zara",
  "snippet": "Реальні відгуки...",
  "url": "https://example.com",
  "position": 1
}
```

### Аналітика

**Отримати статистику:**
```bash
GET /api/statistics
```

Повертає:
- Загальна кількість згадувань
- Розподіл по sentiment (позитив/негатив/нейтрал)
- Розподіл по платформах
- Топ категорії проблем
- Timeline даних
- Reputation score

**Перевірити кризу:**
```bash
GET /api/crisis/check
```

### Генерація відповідей

**Згенерувати відповіді на коментар:**
```bash
POST /api/generate-response
{
  "comment_id": "uuid-коментаря",
  "tones": ["official", "friendly", "tech_support"],
  "tone_adjustment": 0.7
}
```

### Чат

**Запитати про бренд:**
```bash
POST /api/chat
{
  "message": "Які найпоширеніші скарги на Zara?"
}
```

**Пошук по коментарях:**
```bash
GET /api/search/comments?query=оплата&limit=10
```

## 🏗️ Структура проекту

```
brandpulse/
├── app/
│   ├── main.py              # FastAPI додаток
│   ├── models.py            # Pydantic моделі
│   ├── config.py            # Налаштування
│   ├── database.py          # ChromaDB manager
│   ├── analytics.py         # Аналітика та детекція криз
│   └── openai_service.py    # OpenAI інтеграція
├── scripts/
│   └── generate_test_data.py  # Генератор тестових даних
├── requirements.txt
└── .env
```

## 🔥 Crisis Detection Algorithm

Система детектує кризу коли:
1. **Сплеск згадувань** > 3x від baseline (середнього за 30 днів)
2. **Негативні відгуки** > 70%
3. **Критичні keywords**: "crash", "не працює", "scam", "broken", etc.

Рівні кризи:
- 🟢 **LOW** - нормальна ситуація
- 🟡 **MEDIUM** - підвищена увага
- 🟠 **HIGH** - потрібна реакція
- 🔴 **CRITICAL** - негайна дія

## 📊 Demo Scenario

```python
# 1. Генеруємо тестові дані з кризою (вже включено в скрипт)
python scripts/generate_test_data.py

# 2. Перевіряємо кризу
curl http://localhost:8000/api/crisis/check

# 3. Отримуємо статистику
curl http://localhost:8000/api/statistics

# 4. Запитуємо в чаті
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Які проблеми з додатком?"}'
```

## 🎨 Приклади використання

### Моніторинг репутації в реальному часі

```python
import requests

# Перевірка статистики
stats = requests.get("http://localhost:8000/api/statistics").json()
print(f"Reputation Score: {stats['reputation_score']['overall_score']}/100")
print(f"Trend: {stats['reputation_score']['trend']}")
print(f"Risk Level: {stats['reputation_score']['risk_level']}")
```

### Автоматична відповідь на негативний відгук

```python
# 1. Додаємо коментар
response = requests.post("http://localhost:8000/api/comments", json={
    "body": "Додаток не працює!",
    "timestamp": "2025-10-04T15:00:00",
    "rating": 1.0,
    "platform": "app_store",
    "sentiment": "negative",
    "category": "app_crash"
})

comment_id = response.json()["comment_id"]

# 2. Генеруємо відповіді
drafts = requests.post("http://localhost:8000/api/generate-response", json={
    "comment_id": comment_id,
    "tones": ["official", "friendly"],
    "tone_adjustment": 0.6
}).json()

for draft in drafts:
    print(f"\n[{draft['tone'].upper()}]")
    print(draft['text'])
    print(f"Actions: {draft['action_items']}")
```

## 🔧 Конфігурація Crisis Detection

У `app/config.py` можна налаштувати параметри:

```python
CRISIS_SPIKE_MULTIPLIER = 3.0  # Множник для сплеску
CRISIS_NEGATIVE_THRESHOLD = 0.7  # Поріг негативу (70%)
CRISIS_CRITICAL_KEYWORDS = ["crash", "не працює", "scam"]
BASELINE_DAYS = 30  # Період для розрахунку baseline
```

## 📝 Платформи

Підтримувані платформи:
- App Store
- Google Play
- TrustPilot
- Reddit
- Quora
- Google SERP

## 🎯 Тестові дані (Zara)

Генератор створює:
- **~250 коментарів** за 30 днів
- **5 документів** про бренд (FAQ, політики, релізи)
- **4 SERP результати**
- **Симуляцію кризи** (сплеск негативу сьогодні)

## 🚀 Deployment

Для production:
1. Додайте gunicorn: `pip install gunicorn`
2. Запустіть: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
3. Налаштуйте nginx як reverse proxy
4. Додайте моніторинг (Sentry, DataDog)

## 📄 License

MIT License - VibeCodingHackathon 2025
