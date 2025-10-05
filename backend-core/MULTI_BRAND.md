# 🏢 Multi-Brand Support - Документація

## Огляд

Тепер BrandPulse підтримує **множину брендів** з можливістю:
- ✅ Збереження даних для різних брендів
- ✅ Фільтрація по конкретному бренду
- ✅ Порівняння брендів між собою (competitor analysis)
- ✅ Видалення даних по бренду
- ✅ Список всіх брендів в системі

---

## 🔄 Що змінилось

### Раніше:
```json
{
  "text": "Review text...",
  "sentiment": "negative"
}
```
Дані без прив'язки до бренду (хардкод Zara).

### Тепер:
```json
{
  "brand_name": "Zara",
  "text": "Review text...",
  "sentiment": "negative"
}
```
Кожен відгук прив'язаний до бренду.

---

## 📋 Нові ендпоінти

### 1. `GET /api/brands` - Список всіх брендів

```bash
curl http://localhost:8000/api/brands
```

**Відповідь:**
```json
["H&M", "Mango", "Zara"]
```

---

### 2. `DELETE /api/brands/{brand_name}` - Видалити бренд

```bash
curl -X DELETE http://localhost:8000/api/brands/Zara
```

**Відповідь:**
```json
{
  "success": true,
  "brand_name": "Zara",
  "deleted_count": 250,
  "message": "Видалено 250 записів"
}
```

---

### 3. `POST /api/brands/compare` - Порівняння брендів

```bash
POST /api/brands/compare
```

**Request:**
```json
{
  "brand_names": ["Zara", "H&M", "Mango"],
  "date_from": "2025-09-01T00:00:00",
  "date_to": "2025-10-04T23:59:59"
}
```

**Response:**
```json
[
  {
    "brand_name": "Zara",
    "total_mentions": 250,
    "reputation_score": 65.5,
    "sentiment_distribution": {
      "positive": 100,
      "negative": 80,
      "neutral": 70
    },
    "severity_distribution": {
      "low": 120,
      "medium": 80,
      "high": 30,
      "critical": 20
    },
    "top_strengths": [
      "Позитивний sentiment (100 відгуків)",
      "Високий рейтинг (4.2/5)",
      "Активність на app_store (80 згадувань)"
    ],
    "top_weaknesses": [
      "Проблеми з 'оплата' (45 згадувань)",
      "Високий рівень критичних проблем (8%)",
      "Проблеми з 'краш' (25 згадувань)"
    ],
    "platform_performance": {
      "app_store": 80,
      "google_play": 90,
      "trustpilot": 50
    }
  },
  {
    "brand_name": "H&M",
    "total_mentions": 180,
    "reputation_score": 72.3,
    ...
  }
]
```

---

## 🔧 Оновлені ендпоінти

### 1. `POST /api/reviews/external` - Тепер з brand_name

```json
{
  "reviews": [
    {
      "id": "review_001",
      "brand_name": "Zara",  // ← ОБОВ'ЯЗКОВО!
      "source": "appstore",
      "text": "Great app!",
      "rating": 5,
      "created_at": "2025-10-04T15:00:00",
      "sentiment": "позитивний",
      "description": "...",
      "categories": ["інтерфейс"],
      "severity": "low"
    }
  ],
  "count": 1
}
```

---

### 2. `POST /api/reviews/filter` - Фільтр по бренду

```json
{
  "brand_name": "Zara",  // ← Новий фільтр!
  "severity": ["high", "critical"],
  "sentiment": ["negative"],
  "limit": 50
}
```

**Response включає brand_name:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "brand_name": "Zara",  // ← В кожному відгуку
      "text": "...",
      "platform": "app_store",
      "severity": "critical"
    }
  ]
}
```

---

### 3. `POST /api/statistics` - Статистика по бренду

```json
{
  "brand_name": "Zara",  // ← Фільтр по бренду
  "date_from": "2025-10-01T00:00:00",
  "date_to": "2025-10-04T23:59:59"
}
```

---

## 🎯 Use Cases

### 1. Додати дані для нового бренду

```python
import requests

# Додати відгуки для H&M
reviews_hm = {
    "reviews": [
        {
            "id": "hm_001",
            "brand_name": "H&M",
            "source": "appstore",
            "text": "Love the H&M app!",
            "rating": 5,
            "created_at": "2025-10-04T15:00:00",
            "sentiment": "позитивний",
            "description": "Користувач в захваті від додатку",
            "categories": ["інтерфейс", "дизайн"],
            "severity": "low"
        }
    ],
    "count": 1
}

requests.post(
    "http://localhost:8000/api/reviews/external",
    json=reviews_hm
)
```

---

### 2. Порівняти свій бренд з конкурентами

```python
# Порівняння Zara з конкурентами
comparison = requests.post(
    "http://localhost:8000/api/brands/compare",
    json={
        "brand_names": ["Zara", "H&M", "Mango"],
        "date_from": "2025-09-01T00:00:00"
    }
).json()

# Аналіз результатів
for brand in comparison:
    print(f"\n{brand['brand_name']}:")
    print(f"  Reputation: {brand['reputation_score']}/100")
    print(f"  Total mentions: {brand['total_mentions']}")
    
    print(f"\n  💪 Сильні сторони:")
    for strength in brand['top_strengths']:
        print(f"    - {strength}")
    
    print(f"\n  ⚠️ Слабкі сторони:")
    for weakness in brand['top_weaknesses']:
        print(f"    - {weakness}")
```

**Output:**
```
Zara:
  Reputation: 65.5/100
  Total mentions: 250

  💪 Сильні сторони:
    - Позитивний sentiment (100 відгуків)
    - Високий рейтинг (4.2/5)
    - Активність на app_store (80 згадувань)

  ⚠️ Слабкі сторони:
    - Проблеми з 'оплата' (45 згадувань)
    - Високий рівень критичних проблем (8%)

H&M:
  Reputation: 72.3/100
  ...
```

---

### 3. Статистика тільки по своєму бренду

```python
# Статистика Zara за жовтень
zara_stats = requests.post(
    "http://localhost:8000/api/statistics",
    json={
        "brand_name": "Zara",
        "date_from": "2025-10-01T00:00:00",
        "date_to": "2025-10-31T23:59:59"
    }
).json()

print(f"Zara mentions: {zara_stats['total_mentions']}")
print(f"Reputation: {zara_stats['reputation_score']['overall_score']}")
```

---

### 4. Знайти всі критичні проблеми по всіх брендах

```python
# Критичні проблеми незалежно від бренду
all_critical = requests.post(
    "http://localhost:8000/api/reviews/filter",
    json={
        "severity": ["critical"],
        "sentiment": ["negative"]
    }
).json()

# Групуємо по брендах
from collections import defaultdict

by_brand = defaultdict(list)
for review in all_critical["data"]:
    by_brand[review["brand_name"]].append(review)

for brand, reviews in by_brand.items():
    print(f"\n{brand}: {len(reviews)} критичних проблем")
    for review in reviews[:3]:
        print(f"  - {review['text'][:60]}...")
```

---

### 5. Видалити тестовий бренд

```python
# Видалити всі дані Test Brand
result = requests.delete(
    "http://localhost:8000/api/brands/Test%20Brand"
).json()

print(f"Видалено {result['deleted_count']} записів")
```

---

### 6. Competitor Analysis Dashboard

```python
def analyze_competitor(brand_name):
    """Детальний аналіз конкурента"""
    
    # Статистика
    stats = requests.post(
        "http://localhost:8000/api/statistics",
        json={"brand_name": brand_name}
    ).json()
    
    # Критичні проблеми
    critical = requests.post(
        "http://localhost:8000/api/reviews/filter",
        json={
            "brand_name": brand_name,
            "severity": ["critical"],
            "limit": 10
        }
    ).json()
    
    return {
        "brand": brand_name,
        "reputation": stats["reputation_score"]["overall_score"],
        "total_reviews": stats["total_mentions"],
        "critical_issues": critical["pagination"]["filtered_count"],
        "sentiment": stats["sentiment_distribution"],
        "top_problems": stats["top_categories"][:5]
    }

# Аналіз всіх конкурентів
competitors = ["Zara", "H&M", "Mango", "Uniqlo"]
analysis = [analyze_competitor(brand) for brand in competitors]

# Сортуємо по reputation
analysis.sort(key=lambda x: x["reputation"], reverse=True)

print("COMPETITOR RANKING:")
for i, comp in enumerate(analysis, 1):
    print(f"{i}. {comp['brand']}: {comp['reputation']}/100")
    print(f"   Reviews: {comp['total_reviews']}, Critical: {comp['critical_issues']}")
```

---

## 📊 Приклад: Порівняльний звіт

```python
from datetime import datetime, timedelta

# Останній місяць
month_ago = (datetime.now() - timedelta(days=30)).isoformat()

# Порівняння
comparison = requests.post(
    "http://localhost:8000/api/brands/compare",
    json={
        "brand_names": ["Zara", "H&M", "Mango"],
        "date_from": month_ago
    }
).json()

# Генерація звіту
print("=" * 60)
print("COMPETITOR ANALYSIS REPORT")
print("=" * 60)

for brand in comparison:
    print(f"\n{'='*60}")
    print(f"BRAND: {brand['brand_name']}")
    print(f"{'='*60}")
    
    print(f"\n📊 OVERALL:")
    print(f"  Reputation Score: {brand['reputation_score']}/100")
    print(f"  Total Mentions: {brand['total_mentions']}")
    
    print(f"\n😊 SENTIMENT:")
    for sentiment, count in brand['sentiment_distribution'].items():
        pct = (count / brand['total_mentions'] * 100) if brand['total_mentions'] > 0 else 0
        print(f"  {sentiment}: {count} ({pct:.1f}%)")
    
    print(f"\n⚠️ SEVERITY:")
    for severity, count in brand['severity_distribution'].items():
        pct = (count / brand['total_mentions'] * 100) if brand['total_mentions'] > 0 else 0
        print(f"  {severity}: {count} ({pct:.1f}%)")
    
    print(f"\n💪 STRENGTHS:")
    for strength in brand['top_strengths']:
        print(f"  ✓ {strength}")
    
    print(f"\n⚠️ WEAKNESSES:")
    for weakness in brand['top_weaknesses']:
        print(f"  ✗ {weakness}")
    
    print(f"\n📱 PLATFORM PERFORMANCE:")
    for platform, count in brand['platform_performance'].items():
        print(f"  {platform}: {count} mentions")
```

---

## 🔥 Advanced: AI-Powered Insights

```python
# Отримати порівняння
comparison = requests.post(
    "http://localhost:8000/api/brands/compare",
    json={"brand_names": ["Zara", "H&M"]}
).json()

# Запитати AI про інсайти
insights_query = f"""
Порівняй два бренди:

Zara:
- Reputation: {comparison[0]['reputation_score']}
- Сильні сторони: {comparison[0]['top_strengths']}
- Слабкі сторони: {comparison[0]['top_weaknesses']}

H&M:
- Reputation: {comparison[1]['reputation_score']}
- Сильні сторони: {comparison[1]['top_strengths']}
- Слабкі сторони: {comparison[1]['top_weaknesses']}

Дай рекомендації як Zara може покращити свою репутацію.
"""

ai_insights = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": insights_query}
).json()

print(ai_insights["answer"])
```

---

## ✅ Migration Guide

### Для існуючих даних (Zara):

Якщо у вас вже є дані без `brand_name`, вони отримають `brand_name: "Unknown"`. 

**Рекомендація:** Видалити старі дані і додати заново з `brand_name`.

```python
# 1. Видалити Unknown
requests.delete("http://localhost:8000/api/brands/Unknown")

# 2. Додати заново з правильним brand_name
# (використовуй scripts/generate_test_data.py як приклад)
```

---

## 📝 Summary

**Нові можливості:**
- ✅ Multi-brand підтримка
- ✅ Фільтрація по бренду в всіх ендпоінтах
- ✅ Порівняння брендів (`/api/brands/compare`)
- ✅ Управління брендами (`GET/DELETE /api/brands`)
- ✅ Competitor analysis
- ✅ Brand-specific статистика

**Оновлені ендпоінти:**
- `POST /api/reviews/external` - додано `brand_name` (обов'язково)
- `POST /api/reviews/filter` - додано фільтр `brand_name`
- `POST /api/statistics` - додано фільтр `brand_name`

**Нові ендпоінти:**
- `GET /api/brands` - список брендів
- `DELETE /api/brands/{brand_name}` - видалення
- `POST /api/brands/compare` - порівняння

**Готово для competitor analysis та multi-brand моніторингу!** 🚀
