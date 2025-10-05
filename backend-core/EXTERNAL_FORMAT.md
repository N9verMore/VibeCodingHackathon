# Приклад використання ендпоінту /api/reviews/external

## ⚠️ ВАЖЛИВО: Поле називається `categories` (множина)!

### Правильний приклад запиту:

```bash
curl -X POST http://localhost:8000/api/reviews/external \
  -H "Content-Type: application/json" \
  -d '{
    "reviews": [
        {
            "id": "review_001",
            "source": "appstore",
            "backlink": "https://apps.apple.com/review/001",
            "text": "Користуюся вже місяць, все працює відмінно",
            "rating": 5,
            "created_at": "2025-10-02T11:08:15.919438",
            "sentiment": "позитивний",
            "description": "Користувач хвалить додаток",
            "categories": ["інтерфейс", "функціональність"],
            "severity": "low",
            "is_processed": true
        },
        {
            "id": "review_002",
            "source": "googleplay",
            "backlink": "https://play.google.com/review/002",
            "text": "Намагаюся оплатити, але вилітає помилка",
            "rating": 1,
            "created_at": "2025-10-03T11:08:15.919438",
            "sentiment": "негативний",
            "description": "Проблеми з оплатою",
            "categories": ["оплата", "додаток"],
            "severity": "critical",
            "is_processed": true
        }
    ],
    "count": 2
  }'
```

## Маппінг полів:

| Ваше поле | Внутрішнє поле | Тип | Примітки |
|-----------|----------------|-----|----------|
| `text` | `body` | string | Текст коментаря |
| `created_at` | `timestamp` | datetime | Автоматична конвертація ISO формату |
| `rating` | `rating` | int | 1-5 |
| `source` | `platform` | string | appstore → app_store, googleplay → google_play |
| `sentiment` | `sentiment` | string | позитивний → positive, негативний → negative |
| `description` | `llm_description` | string | Опис від LLM |
| **`categories`** | `category` | **List[string]** | **МАСИВ категорій** (["оплата", "додаток"]) |
| `severity` | `severity` | string | low, medium, high, critical |
| `backlink` | `backlink` | string | Посилання на відгук |

## ✅ Правильно:

```json
{
  "categories": ["оплата", "додаток", "краш"]
}
```

## ❌ Неправильно:

```json
{
  "category": ["оплата", "додаток"]  // Має бути categories!
}
```

## Повний приклад з вашими даними:

```json
{
  "reviews": [
    {
      "id": "review_001",
      "source": "appstore",
      "backlink": "https://apps.apple.com/review/001",
      "text": "Користуюся вже місяць, все працює відмінно.",
      "rating": 5,
      "created_at": "2025-10-02T11:08:15.919438",
      "sentiment": "позитивний",
      "description": "Користувач хвалить додаток",
      "categories": ["інтерфейс", "функціональність"],
      "severity": "low",
      "is_processed": true
    },
    {
      "id": "review_002",
      "source": "googleplay",
      "backlink": "https://play.google.com/review/002",
      "text": "Намагаюся оплатити преміум підписку, але постійно вилітає помилка",
      "rating": 1,
      "created_at": "2025-10-03T11:08:15.919438",
      "sentiment": "негативний",
      "description": "Користувач не може оплатити через помилки",
      "categories": ["оплата"],
      "severity": "critical",
      "is_processed": true
    }
  ],
  "count": 2
}
```

## Python приклад:

```python
import requests

reviews_data = {
    "reviews": [
        {
            "id": "review_001",
            "source": "appstore",
            "backlink": "https://apps.apple.com/review/001",
            "text": "Додаток крашиться при оплаті!",
            "rating": 1,
            "created_at": "2025-10-04T15:00:00",
            "sentiment": "негативний",
            "description": "Краш при оплаті",
            "categories": ["оплата", "краш", "додаток"],  # categories!
            "severity": "critical",
            "is_processed": True
        }
    ],
    "count": 1
}

response = requests.post(
    "http://localhost:8000/api/reviews/external",
    json=reviews_data
)

print(response.json())
# {
#   "success": True,
#   "added_count": 1,
#   "comment_ids": ["uuid"],
#   "message": "Успішно додано 1 відгуків"
# }
```

## Severity levels:

- `low` - незначні проблеми або позитивні відгуки
- `medium` - помірні проблеми, потребують уваги
- `high` - серйозні проблеми, потребують швидкої реакції
- `critical` - критичні проблеми (краші, втрата даних, шахрайство)

## Після додавання відгуків:

```bash
# Отримати статистику
GET /api/statistics

# Результат включає severity_distribution:
{
  "severity_distribution": {
    "low": 120,
    "medium": 80,
    "high": 30,
    "critical": 20
  },
  "top_categories": [
    {"category": "оплата", "count": 45},
    {"category": "додаток", "count": 38}
  ]
}
```
