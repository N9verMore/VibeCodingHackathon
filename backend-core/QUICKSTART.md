# 🚀 QUICK START GUIDE - BrandPulse

## Крок 1: Установка (2 хвилини)

```bash
# Встановити залежності
pip install -r requirements.txt

# Налаштувати .env файл
cp .env.example .env
# Додайте ваш OpenAI API key в .env файл
```

## Крок 2: Генерація тестових даних (1 хвилина)

```bash
python scripts/generate_test_data.py
```

Це створить:
- 250+ коментарів про Zara за 30 днів
- 5 документів про бренд
- 4 результати з Google SERP
- Симуляцію кризи (сьогодні багато негативу)

## Крок 3: Запуск API (1 секунда)

```bash
python app/main.py
```

API запуститься на `http://localhost:8000`

Документація: `http://localhost:8000/docs`

## Крок 4: Демо (опціонально)

```bash
# Запустити live crisis simulation
python scripts/crisis_demo.py
```

## 🎯 Основні API запити

### Отримати статистику
```bash
curl http://localhost:8000/api/statistics
```

### Перевірити кризу
```bash
curl http://localhost:8000/api/crisis/check
```

### Запитати в чаті
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Які найпоширеніші проблеми?"}'
```

### Додати коментар
```bash
curl -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Дуже задоволений якістю!",
    "timestamp": "2025-10-04T15:00:00",
    "rating": 5.0,
    "platform": "trustpilot",
    "sentiment": "positive",
    "category": "quality"
  }'
```

### Згенерувати відповідь
```bash
# Спочатку знайти ID коментаря
curl "http://localhost:8000/api/search/comments?query=crash&limit=1"

# Потім згенерувати відповідь
curl -X POST http://localhost:8000/api/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "comment_id": "ваш-comment-id",
    "tones": ["official", "friendly"]
  }'
```

## 📊 Що показати на демо

1. **Статистика в реальному часі**
   - Reputation Score: 0-100
   - Розподіл sentiment
   - Платформи з найбільшим негативом

2. **Crisis Detection**
   - Automatic spike detection
   - Critical keywords
   - AI recommendations

3. **AI Response Generator**
   - 3 стилі відповідей
   - Action items
   - Tone adjustment slider

4. **Smart Chat**
   - "Які проблеми з додатком?"
   - "Скільки негативних відгуків сьогодні?"
   - "Що пишуть про доставку?"

## 🔥 Killer Demo Flow

```bash
# 1. Показати початкову статистику
curl http://localhost:8000/api/statistics

# 2. Запустити кризу в реальному часі
python scripts/crisis_demo.py

# 3. Показати як система виявила кризу
# 4. Згенерувати відповіді на проблемні коментарі
# 5. Продемонструвати Smart Chat
```

## 🐛 Troubleshooting

**Помилка: OpenAI API key not found**
- Додайте ваш ключ в `.env` файл

**Помилка: ChromaDB не запускається**
- Видаліть папку `chroma_db` та запустіть заново

**API не запускається**
- Перевірте чи порт 8000 вільний
- Змініть PORT в `.env` файлі

## 📝 Endpoints для фронтенду

| Endpoint | Method | Опис |
|----------|--------|------|
| `/api/statistics` | GET | Повна статистика |
| `/api/reputation-score` | GET | Reputation health score |
| `/api/crisis/check` | GET | Перевірка кризи |
| `/api/chat` | POST | Чат з AI |
| `/api/comments` | POST | Додати коментар |
| `/api/generate-response` | POST | Генерація відповідей |
| `/api/search/comments` | GET | Пошук коментарів |

## 🎨 Response Examples

### Statistics Response
```json
{
  "total_mentions": 250,
  "sentiment_distribution": {
    "positive": 100,
    "neutral": 50,
    "negative": 100
  },
  "reputation_score": {
    "overall_score": 65.5,
    "trend": "down",
    "risk_level": "medium"
  }
}
```

### Crisis Alert
```json
{
  "crisis_detected": true,
  "alert": {
    "crisis_level": "high",
    "affected_count": 25,
    "critical_keywords": ["crash", "payment"],
    "recommendations": [
      "Перевірити платіжну систему",
      "Підготувати офіційну заяву"
    ]
  }
}
```

## 🚀 Production Deployment

```bash
# Використати gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 Додаткова інформація

- Документація API: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
- GitHub: [your-repo]
- Презентація: [slides-link]
