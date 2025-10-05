# 📊 Статистика з фільтрами - Документація

## Ендпоінти статистики

### 1. `POST /api/statistics` - З фільтрами
Отримати статистику з фільтрацією по даті та платформах

---

## 📋 Приклади використання


---

### 2️⃣ Статистика за останній тиждень (POST)

```bash
curl -X POST http://localhost:8000/api/statistics \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2025-09-27T00:00:00",
    "date_to": "2025-10-04T23:59:59"
  }'
```

---

### 3️⃣ Статистика тільки з App Store та Google Play

```bash
curl -X POST http://localhost:8000/api/statistics \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["app_store", "google_play"]
  }'
```

---

### 4️⃣ Статистика за жовтень з конкретних платформ

```bash
curl -X POST http://localhost:8000/api/statistics \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2025-10-01T00:00:00",
    "date_to": "2025-10-31T23:59:59",
    "platforms": ["app_store", "google_play", "trustpilot"]
  }'
```

---

## 🔧 Доступні фільтри

### **date_from** (string, ISO format)
Початкова дата для фільтрації

```json
{
  "date_from": "2025-10-01T00:00:00"
}
```

### **date_to** (string, ISO format)
Кінцева дата для фільтрації

```json
{
  "date_to": "2025-10-04T23:59:59"
}
```

### **platforms** (List[string])
Список платформ для фільтрації

Доступні значення:
- `"app_store"`
- `"google_play"`
- `"trustpilot"`
- `"reddit"`
- `"quora"`

```json
{
  "platforms": ["app_store", "google_play"]
}
```

---

## 🎯 Use Cases

### 1. Порівняння статистики по періодах

```python
import requests
from datetime import datetime, timedelta

# Статистика за попередній тиждень
last_week_start = (datetime.now() - timedelta(days=14)).isoformat()
last_week_end = (datetime.now() - timedelta(days=7)).isoformat()

last_week = requests.post(
    "http://localhost:8000/api/statistics",
    json={
        "date_from": last_week_start,
        "date_to": last_week_end
    }
).json()

# Статистика за поточний тиждень
this_week_start = (datetime.now() - timedelta(days=7)).isoformat()
this_week_end = datetime.now().isoformat()

this_week = requests.post(
    "http://localhost:8000/api/statistics",
    json={
        "date_from": this_week_start,
        "date_to": this_week_end
    }
).json()

# Порівняння
print(f"Попередній тиждень: {last_week['total_mentions']} згадувань")
print(f"Поточний тиждень: {this_week['total_mentions']} згадувань")
print(f"Зміна: {this_week['total_mentions'] - last_week['total_mentions']}")
```

### 2. Аналіз по платформах

```python
# App Store
app_store_stats = requests.post(
    "http://localhost:8000/api/statistics",
    json={"platforms": ["app_store"]}
).json()

# Google Play
google_play_stats = requests.post(
    "http://localhost:8000/api/statistics",
    json={"platforms": ["google_play"]}
).json()

print(f"App Store:")
print(f"  Reputation: {app_store_stats['reputation_score']['overall_score']}")
print(f"  Негатив: {app_store_stats['sentiment_distribution']['negative']}")

print(f"\nGoogle Play:")
print(f"  Reputation: {google_play_stats['reputation_score']['overall_score']}")
print(f"  Негатив: {google_play_stats['sentiment_distribution']['negative']}")
```

### 3. Щомісячний звіт

```python
# Статистика за поточний місяць
from datetime import datetime

month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0).isoformat()
month_end = datetime.now().isoformat()

monthly_stats = requests.post(
    "http://localhost:8000/api/statistics",
    json={
        "date_from": month_start,
        "date_to": month_end
    }
).json()

# Генерація звіту
report = f"""
ЩОМІСЯЧНИЙ ЗВІТ

Період: {month_start[:10]} - {month_end[:10]}
Всього згадувань: {monthly_stats['total_mentions']}

Sentiment:
- Позитивні: {monthly_stats['sentiment_distribution']['positive']}
- Негативні: {monthly_stats['sentiment_distribution']['negative']}
- Нейтральні: {monthly_stats['sentiment_distribution']['neutral']}

Reputation Score: {monthly_stats['reputation_score']['overall_score']}/100
Тренд: {monthly_stats['reputation_score']['trend']}
Рівень ризику: {monthly_stats['reputation_score']['risk_level']}

Топ проблеми:
"""

for cat in monthly_stats['top_categories'][:5]:
    report += f"- {cat['category']}: {cat['count']} згадувань\n"

print(report)
```

### 4. Dashboard з real-time filters

```python
# Отримати статистику за останні 24 години
from datetime import datetime, timedelta

day_ago = (datetime.now() - timedelta(days=1)).isoformat()

realtime_stats = requests.post(
    "http://localhost:8000/api/statistics",
    json={
        "date_from": day_ago
    }
).json()

print(f"За останні 24 години:")
print(f"Згадувань: {realtime_stats['total_mentions']}")
print(f"Reputation: {realtime_stats['reputation_score']['overall_score']}")
print(f"Critical issues: {realtime_stats['severity_distribution']['critical']}")
```

---

## 🔥 Комбінування з іншими ендпоінтами

### Приклад: Статистика + Фільтрація відгуків

```python
# 1. Отримати статистику за тиждень
week_stats = requests.post(
    "http://localhost:8000/api/statistics",
    json={
        "date_from": "2025-09-27T00:00:00",
        "date_to": "2025-10-04T23:59:59"
    }
).json()

print(f"Критичних проблем: {week_stats['severity_distribution']['critical']}")

# 2. Якщо є критичні - отримати деталі
if week_stats['severity_distribution']['critical'] > 0:
    critical_reviews = requests.post(
        "http://localhost:8000/api/reviews/filter",
        json={
            "severity": ["critical"],
            "date_from": "2025-09-27T00:00:00",
            "date_to": "2025-10-04T23:59:59"
        }
    ).json()
    
    print(f"\nКритичні відгуки:")
    for review in critical_reviews["data"][:5]:
        print(f"- {review['text'][:80]}...")
```

---

## 📊 Приклад: Порівняння платформ

```python
platforms = ["app_store", "google_play", "trustpilot"]
comparison = {}

for platform in platforms:
    stats = requests.post(
        "http://localhost:8000/api/statistics",
        json={"platforms": [platform]}
    ).json()
    
    comparison[platform] = {
        "total": stats["total_mentions"],
        "reputation": stats["reputation_score"]["overall_score"],
        "negative_ratio": stats["sentiment_distribution"]["negative"] / stats["total_mentions"] if stats["total_mentions"] > 0 else 0
    }

# Виведення порівняння
print("\nПОРІВНЯННЯ ПЛАТФОРМ:")
print(f"{'Платформа':<15} {'Згадувань':<12} {'Reputation':<12} {'% Негативу'}")
print("-" * 60)

for platform, data in comparison.items():
    print(f"{platform:<15} {data['total']:<12} {data['reputation']:<12.1f} {data['negative_ratio']*100:.1f}%")
```

---

## ⚡ Tips & Best Practices

### 1. Кешування для Dashboard
```python
import time

cache = {}
cache_duration = 300  # 5 хвилин

def get_cached_stats(filters=None):
    cache_key = str(filters) if filters else "all"
    
    if cache_key in cache:
        cached_time, cached_data = cache[cache_key]
        if time.time() - cached_time < cache_duration:
            return cached_data
    
    # Отримати свіжі дані
    if filters:
        data = requests.post(
            "http://localhost:8000/api/statistics",
            json=filters
        ).json()
    else:
        data = requests.get("http://localhost:8000/api/statistics").json()
    
    cache[cache_key] = (time.time(), data)
    return data
```

### 2. Автоматичні щоденні звіти
```python
from datetime import datetime, timedelta
import schedule

def daily_report():
    yesterday = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0)
    today = datetime.now().replace(hour=0, minute=0)
    
    stats = requests.post(
        "http://localhost:8000/api/statistics",
        json={
            "date_from": yesterday.isoformat(),
            "date_to": today.isoformat()
        }
    ).json()
    
    # Відправити звіт (email, Slack, etc.)
    send_report(stats)

# Запускати щодня о 9:00
schedule.every().day.at("09:00").do(daily_report)
```

---

## 🎨 Frontend приклад (React)

```jsx
import { useState, useEffect } from 'react';

function StatisticsDashboard() {
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({
    date_from: null,
    date_to: null,
    platforms: []
  });

  const fetchStats = async () => {
    const hasFilters = filters.date_from || filters.date_to || filters.platforms.length > 0;
    
    if (hasFilters) {
      // POST з фільтрами
      const response = await fetch('http://localhost:8000/api/statistics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
      const data = await response.json();
      setStats(data);
    } else {
      // GET без фільтрів
      const response = await fetch('http://localhost:8000/api/statistics');
      const data = await response.json();
      setStats(data);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [filters]);

  if (!stats) return <div>Loading...</div>;

  return (
    <div>
      <h1>Статистика бренду</h1>
      
      {/* Фільтри */}
      <div className="filters">
        <input 
          type="date" 
          onChange={(e) => setFilters({...filters, date_from: e.target.value + 'T00:00:00'})}
        />
        <input 
          type="date" 
          onChange={(e) => setFilters({...filters, date_to: e.target.value + 'T23:59:59'})}
        />
        {/* Вибір платформ... */}
      </div>

      {/* Статистика */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Всього згадувань</h3>
          <p className="big-number">{stats.total_mentions}</p>
        </div>
        
        <div className="stat-card">
          <h3>Reputation Score</h3>
          <p className="big-number">{stats.reputation_score.overall_score}/100</p>
          <span className={`trend trend-${stats.reputation_score.trend}`}>
            {stats.reputation_score.trend === 'up' ? '↑' : stats.reputation_score.trend === 'down' ? '↓' : '→'}
          </span>
        </div>
        
        <div className="stat-card">
          <h3>Risk Level</h3>
          <span className={`badge badge-${stats.reputation_score.risk_level}`}>
            {stats.reputation_score.risk_level}
          </span>
        </div>
      </div>

      {/* Діаграми... */}
    </div>
  );
}
```

---

## ✅ Summary

**GET /api/statistics** - Загальна статистика
```bash
curl http://localhost:8000/api/statistics
```

**POST /api/statistics** - З фільтрами
```bash
curl -X POST http://localhost:8000/api/statistics \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2025-10-01T00:00:00",
    "date_to": "2025-10-04T23:59:59",
    "platforms": ["app_store", "google_play"]
  }'
```

**Доступні фільтри:**
- ✅ `date_from` - початкова дата
- ✅ `date_to` - кінцева дата
- ✅ `platforms` - список платформ

**Використання:**
- 📊 Порівняння періодів
- 📈 Аналіз по платформах
- 📅 Щомісячні звіти
- ⚡ Real-time dashboard
