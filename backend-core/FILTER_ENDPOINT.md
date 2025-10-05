# 🔍 Фільтрація відгуків - Документація

## Ендпоінт: `POST /api/reviews/filter`

Гнучка фільтрація відгуків за множинними критеріями з пагінацією та сортуванням.

---

## 📋 Приклади використання

### 1️⃣ Відгуки високої та критичної серйозності

```bash
curl -X POST http://localhost:8000/api/reviews/filter \
  -H "Content-Type: application/json" \
  -d '{
    "severity": ["high", "critical"],
    "limit": 50
  }'
```

**Відповідь:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid-1",
      "text": "Додаток крашиться при оплаті!",
      "platform": "app_store",
      "sentiment": "negative",
      "severity": "critical",
      "category": "оплата, краш, додаток",
      "rating": 1.0,
      "timestamp": "2025-10-04T15:00:00",
      "backlink": "https://apps.apple.com/review/123"
    }
  ],
  "pagination": {
    "total": 250,
    "filtered_count": 25,
    "returned_count": 25,
    "offset": 0,
    "limit": 50,
    "has_more": false
  }
}
```

---

### 2️⃣ Негативні відгуки з категорією "оплата"

```bash
curl -X POST http://localhost:8000/api/reviews/filter \
  -H "Content-Type: application/json" \
  -d '{
    "sentiment": ["negative"],
    "categories": ["оплата"],
    "sort_by": "severity",
    "sort_order": "desc"
  }'
```

---

### 3️⃣ Критичні проблеми за останній тиждень

```bash
curl -X POST http://localhost:8000/api/reviews/filter \
  -H "Content-Type: application/json" \
  -d '{
    "severity": ["critical"],
    "date_from": "2025-09-27T00:00:00",
    "date_to": "2025-10-04T23:59:59",
    "sort_by": "timestamp",
    "sort_order": "desc"
  }'
```

---

### 4️⃣ Негативні відгуки з App Store з низьким рейтингом

```bash
curl -X POST http://localhost:8000/api/reviews/filter \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["app_store"],
    "sentiment": ["negative"],
    "rating_max": 2.0,
    "limit": 20
  }'
```

---

### 5️⃣ Всі проблеми з категоріями "оплата" або "краш"

```bash
curl -X POST http://localhost:8000/api/reviews/filter \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["оплата", "краш"],
    "severity": ["high", "critical"]
  }'
```

**Примітка:** Фільтр `categories` працює як **OR** - повертає відгуки де **хоча б одна** категорія збігається.

---

### 6️⃣ Пагінація - друга сторінка

```bash
curl -X POST http://localhost:8000/api/reviews/filter \
  -H "Content-Type: application/json" \
  -d '{
    "severity": ["high", "critical"],
    "limit": 20,
    "offset": 20
  }'
```

---

## 🔧 Всі доступні фільтри

### **severity** (List[string])
Рівень серйозності: `"low"`, `"medium"`, `"high"`, `"critical"`

```json
{
  "severity": ["high", "critical"]
}
```

### **sentiment** (List[string])
Настрій: `"positive"`, `"negative"`, `"neutral"`

```json
{
  "sentiment": ["negative"]
}
```

### **categories** (List[string])
Категорії (OR логіка - хоча б одна збігається)

```json
{
  "categories": ["оплата", "краш", "доставка"]
}
```

### **platforms** (List[string])
Платформи: `"app_store"`, `"google_play"`, `"trustpilot"`, `"reddit"`, `"quora"`

```json
{
  "platforms": ["app_store", "google_play"]
}
```

### **rating_min / rating_max** (float)
Діапазон рейтингу (0-5)

```json
{
  "rating_min": 1.0,
  "rating_max": 2.5
}
```

### **date_from / date_to** (string, ISO format)
Діапазон дат

```json
{
  "date_from": "2025-10-01T00:00:00",
  "date_to": "2025-10-04T23:59:59"
}
```

### **limit** (int, 1-1000)
Максимальна кількість результатів (за замовчуванням: 100)

```json
{
  "limit": 50
}
```

### **offset** (int, ≥0)
Зміщення для пагінації (за замовчуванням: 0)

```json
{
  "offset": 20
}
```

### **sort_by** (string)
Сортування: `"timestamp"`, `"rating"`, `"severity"` (за замовчуванням: `"timestamp"`)

```json
{
  "sort_by": "severity"
}
```

### **sort_order** (string)
Порядок: `"asc"`, `"desc"` (за замовчуванням: `"desc"`)

```json
{
  "sort_order": "desc"
}
```

---

## 📊 Структура відповіді

```json
{
  "success": true,
  "data": [
    {
      "id": "comment-uuid",
      "text": "Текст коментаря...",
      "platform": "app_store",
      "sentiment": "negative",
      "severity": "critical",
      "category": "оплата, краш",
      "rating": 1.0,
      "timestamp": "2025-10-04T15:00:00",
      "backlink": "https://..."
    }
  ],
  "pagination": {
    "total": 250,              // Всього коментарів в БД
    "filtered_count": 45,      // Коментарів після фільтрації
    "returned_count": 20,      // Повернуто в цьому запиті
    "offset": 0,               // Поточне зміщення
    "limit": 20,               // Ліміт на сторінку
    "has_more": true           // Чи є ще результати
  },
  "filters_applied": {
    "severity": ["high", "critical"],
    "sentiment": ["negative"]
  }
}
```

---

## 🎯 Use Cases (Сценарії використання)

### 1. Dashboard "На що звернути увагу"

```python
import requests

# Отримати критичні проблеми
response = requests.post(
    "http://localhost:8000/api/reviews/filter",
    json={
        "severity": ["high", "critical"],
        "sentiment": ["negative"],
        "sort_by": "severity",
        "limit": 10
    }
)

critical_issues = response.json()["data"]
print(f"⚠️ Критичних проблем: {len(critical_issues)}")
```

### 2. Моніторинг конкретної категорії

```python
# Всі проблеми з оплатою
payment_issues = requests.post(
    "http://localhost:8000/api/reviews/filter",
    json={
        "categories": ["оплата"],
        "sentiment": ["negative"],
        "date_from": "2025-10-01T00:00:00"
    }
).json()
```

### 3. Експорт негативних відгуків для аналізу

```python
# Пагінація для експорту всіх негативних відгуків
all_negative = []
offset = 0
limit = 100

while True:
    response = requests.post(
        "http://localhost:8000/api/reviews/filter",
        json={
            "sentiment": ["negative"],
            "offset": offset,
            "limit": limit
        }
    ).json()
    
    all_negative.extend(response["data"])
    
    if not response["pagination"]["has_more"]:
        break
    
    offset += limit

print(f"Всього негативних відгуків: {len(all_negative)}")
```

### 4. Пошук проблем на конкретній платформі

```python
# Google Play високої серйозності
google_play_issues = requests.post(
    "http://localhost:8000/api/reviews/filter",
    json={
        "platforms": ["google_play"],
        "severity": ["high", "critical"],
        "sort_by": "timestamp"
    }
).json()
```

---

## 🔥 Комбіновані фільтри

### Приклад: "Найгірші відгуки з App Store за тиждень"

```json
{
  "platforms": ["app_store"],
  "severity": ["critical"],
  "sentiment": ["negative"],
  "rating_max": 2.0,
  "date_from": "2025-09-27T00:00:00",
  "sort_by": "severity",
  "limit": 50
}
```

### Приклад: "Проблеми з оплатою або крашами"

```json
{
  "categories": ["оплата", "краш"],
  "severity": ["high", "critical"],
  "sort_by": "timestamp",
  "sort_order": "desc"
}
```

### Приклад: "Середні проблеми для моніторингу"

```json
{
  "severity": ["medium"],
  "platforms": ["app_store", "google_play"],
  "date_from": "2025-10-01T00:00:00",
  "sort_by": "rating",
  "limit": 100
}
```

---

## ⚡ Performance Tips

1. **Використовуйте пагінацію** для великих датасетів
2. **Фільтруйте по даті** для швидшого пошуку
3. **Обмежуйте limit** до розумних значень (20-100)
4. **Кешуйте результати** на фронтенді якщо можливо

---

## 🐛 Troubleshooting

### Порожні результати?
- Перевірте чи є дані: `GET /api/statistics`
- Перевірте правильність фільтрів (case-sensitive!)
- Спробуйте без фільтрів: `{}`

### Повільний запит?
- Додайте фільтри по даті
- Зменшіть limit
- Використовуйте конкретні фільтри замість широких

---

## 📝 Приклад повного запиту

```python
import requests
from datetime import datetime, timedelta

# Останні 7 днів, критичні проблеми, негатив
week_ago = (datetime.now() - timedelta(days=7)).isoformat()

response = requests.post(
    "http://localhost:8000/api/reviews/filter",
    json={
        "severity": ["high", "critical"],
        "sentiment": ["negative"],
        "date_from": week_ago,
        "sort_by": "severity",
        "sort_order": "desc",
        "limit": 20
    }
)

data = response.json()

print(f"Знайдено: {data['pagination']['filtered_count']} відгуків")
print(f"Показано: {data['pagination']['returned_count']}")

for review in data["data"]:
    print(f"\n⚠️ [{review['severity'].upper()}] {review['platform']}")
    print(f"   {review['text'][:100]}...")
    print(f"   Rating: {review['rating']}, Categories: {review['category']}")
```

---

## 🎨 Frontend приклад (React)

```jsx
import { useState } from 'react';

function ReviewsFilter() {
  const [filters, setFilters] = useState({
    severity: ['high', 'critical'],
    sentiment: ['negative'],
    limit: 20
  });
  const [reviews, setReviews] = useState([]);
  const [pagination, setPagination] = useState(null);

  const fetchReviews = async () => {
    const response = await fetch('http://localhost:8000/api/reviews/filter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters)
    });
    
    const data = await response.json();
    setReviews(data.data);
    setPagination(data.pagination);
  };

  return (
    <div>
      <h2>Фільтрація відгуків</h2>
      
      {/* Фільтри */}
      <div>
        <label>
          <input 
            type="checkbox" 
            checked={filters.severity?.includes('critical')}
            onChange={(e) => {/* toggle critical */}}
          />
          Critical
        </label>
        {/* інші фільтри... */}
      </div>

      <button onClick={fetchReviews}>Застосувати фільтри</button>

      {/* Результати */}
      <div>
        <p>Знайдено: {pagination?.filtered_count} з {pagination?.total}</p>
        {reviews.map(review => (
          <div key={review.id} className={`review-${review.severity}`}>
            <span className="badge">{review.severity}</span>
            <p>{review.text}</p>
            <small>{review.platform} • {review.timestamp}</small>
          </div>
        ))}
      </div>

      {/* Пагінація */}
      {pagination?.has_more && (
        <button onClick={() => {
          setFilters({...filters, offset: filters.offset + filters.limit});
          fetchReviews();
        }}>
          Завантажити більше
        </button>
      )}
    </div>
  );
}
```

---

## 🔗 Інтеграція з іншими ендпоінтами

### Комбо 1: Фільтр + Генерація відповіді

```python
# 1. Знайти критичні негативні відгуки
critical = requests.post(
    "http://localhost:8000/api/reviews/filter",
    json={"severity": ["critical"], "limit": 10}
).json()

# 2. Згенерувати відповіді для кожного
for review in critical["data"]:
    responses = requests.post(
        "http://localhost:8000/api/generate-response",
        json={
            "comment_id": review["id"],
            "tones": ["official", "friendly"]
        }
    ).json()
    
    print(f"Відповідь для: {review['text'][:50]}...")
    print(responses[0]["text"])
```

### Комбо 2: Фільтр + Статистика

```python
# Отримати статистику по критичних відгуках
critical = requests.post(
    "http://localhost:8000/api/reviews/filter",
    json={"severity": ["critical"]}
).json()

print(f"Критичних відгуків: {critical['pagination']['filtered_count']}")

# Порівняти з загальною статистикою
stats = requests.get("http://localhost:8000/api/statistics").json()
percentage = (critical['pagination']['filtered_count'] / stats['total_mentions']) * 100
print(f"Це {percentage:.1f}% від усіх відгуків")
```

---

## ✅ Готово!

Тепер у вас є потужний ендпоінт для фільтрації відгуків з:
- ✅ Множинними фільтрами (severity, sentiment, categories, etc)
- ✅ Пагінацією
- ✅ Сортуванням
- ✅ Гнучкою комбінацією параметрів
- ✅ Детальною інформацією про результати

**Endpoint:** `POST /api/reviews/filter`

Використовуйте його для:
- 📊 Dashboards з критичними проблемами
- 🔍 Пошуку специфічних відгуків
- 📈 Аналізу трендів
- 🎯 Пріоритизації роботи команди
