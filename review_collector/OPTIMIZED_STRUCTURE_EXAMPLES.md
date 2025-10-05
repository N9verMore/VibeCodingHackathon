# Оптимізована структура запитів для Report Generation

## 📋 Загальна структура

```json
POST /generate-report
{
  "brand": "string (required)",
  "appstore": { ... },
  "googleplay": { ... },
  "trustpilot": { ... },
  "reddit": { ... },
  "news": { ... },
  "limit": 50,
  "processing_endpoint_url": "https://your-api.com/process"
}
```

---

## 🎯 Приклади запитів

### 1️⃣ Повний запит (всі джерела)

```json
{
  "brand": "Telegram",
  "appstore": {
    "id": "544007664",
    "country": "us"
  },
  "googleplay": {
    "package_name": "org.telegram.messenger",
    "country": "us"
  },
  "trustpilot": {
    "domain": "telegram.org"
  },
  "reddit": {
    "keywords": "telegram app",
    "days_back": 30,
    "sort": "new"
  },
  "news": {
    "keywords": "Telegram messaging",
    "search_type": "everything",
    "from_date": "2024-10-01",
    "to_date": "2024-10-05",
    "language": "en"
  },
  "limit": 50,
  "processing_endpoint_url": "https://webhook.site/your-endpoint"
}
```

### 2️⃣ Мінімальний запит (тільки Reddit і News)

```json
{
  "brand": "Tesla",
  "reddit": {
    "keywords": "Tesla Model 3"
  },
  "news": {
    "keywords": "Tesla electric vehicle"
  },
  "limit": 100
}
```

### 3️⃣ Тільки App Stores (iOS + Android)

```json
{
  "brand": "Spotify",
  "appstore": {
    "id": "324684580"
  },
  "googleplay": {
    "package_name": "com.spotify.music"
  },
  "limit": 200
}
```

### 4️⃣ Тільки соціальні джерела (Reddit + News)

```json
{
  "brand": "Nike",
  "reddit": {
    "keywords": "Nike shoes",
    "days_back": 7,
    "sort": "hot"
  },
  "news": {
    "keywords": "Nike sports innovation",
    "search_type": "top-headlines",
    "country": "us",
    "category": "sports"
  },
  "limit": 75
}
```

---

## 📖 Детальний опис полів

### Загальні поля

| Поле | Тип | Обов'язкове | Опис |
|------|-----|-------------|------|
| `brand` | string | ✅ Так | Назва бренду для збереження в БД |
| `limit` | integer | ❌ Ні (default: 50) | Глобальний ліміт для всіх джерел |
| `processing_endpoint_url` | string | ❌ Ні | URL для відправки результатів після збору |

### App Store (`appstore`)

| Поле | Тип | Обов'язкове | Опис |
|------|-----|-------------|------|
| `id` | string | ✅ Так | Числовий ID додатку в App Store |
| `country` | string | ❌ Ні (default: "us") | Код країни (us, uk, de, тощо) |

**Приклад:**
```json
"appstore": {
  "id": "544007664",
  "country": "uk"
}
```

### Google Play (`googleplay`)

| Поле | Тип | Обов'язкове | Опис |
|------|-----|-------------|------|
| `package_name` | string | ✅ Так | Package name Android додатку |
| `country` | string | ❌ Ні (default: "us") | Код країни |

**Приклад:**
```json
"googleplay": {
  "package_name": "org.telegram.messenger",
  "country": "de"
}
```

### Trustpilot (`trustpilot`)

| Поле | Тип | Обов'язкове | Опис |
|------|-----|-------------|------|
| `domain` | string | ✅ Так | Домен компанії (e.g., "tesla.com") |

**Приклад:**
```json
"trustpilot": {
  "domain": "booking.com"
}
```

### Reddit (`reddit`)

| Поле | Тип | Обов'язкове | Опис |
|------|-----|-------------|------|
| `keywords` | string | ✅ Так | Ключові слова для пошуку |
| `days_back` | integer | ❌ Ні (default: 30) | Скільки днів назад шукати (1-365) |
| `sort` | string | ❌ Ні (default: "new") | Сортування: new/hot/top/relevance |

**Приклад:**
```json
"reddit": {
  "keywords": "iPhone 15 review",
  "days_back": 14,
  "sort": "top"
}
```

### News (`news`)

| Поле | Тип | Обов'язкове | Опис |
|------|-----|-------------|------|
| `keywords` | string | ✅ Так | Ключові слова для пошуку в новинах |
| `search_type` | string | ❌ Ні (default: "everything") | everything / top-headlines |
| `from_date` | string | ❌ Ні | Дата початку (YYYY-MM-DD) |
| `to_date` | string | ❌ Ні | Дата кінця (YYYY-MM-DD) |
| `language` | string | ❌ Ні (default: "en") | Код мови (en, uk, de, тощо) |
| `country` | string | ❌ Ні | Код країни (тільки для top-headlines) |
| `category` | string | ❌ Ні | Категорія: business/entertainment/general/health/science/sports/technology |
| `sources` | string | ❌ Ні | ID джерел через кому (тільки для top-headlines) |

**Приклад 1 (everything):**
```json
"news": {
  "keywords": "artificial intelligence",
  "search_type": "everything",
  "from_date": "2024-09-01",
  "to_date": "2024-10-05",
  "language": "en"
}
```

**Приклад 2 (top-headlines):**
```json
"news": {
  "keywords": "technology",
  "search_type": "top-headlines",
  "country": "us",
  "category": "technology"
}
```

---

## 🔄 Як працює пошук vs збереження

### App Store / Google Play / Trustpilot
- **ID для пошуку:** береться з відповідного поля (`id`, `package_name`, `domain`)
- **Зберігається в БД як:** `brand` (з верхнього рівня)

### Reddit
- **Пошук:** за `reddit.keywords`
- **Зберігається в БД як:** `brand` (з верхнього рівня)

### News
- **Пошук в NewsAPI:** за `news.keywords`
- **Зберігається в БД як:** `brand` (з верхнього рівня)

**Приклад:**
```json
{
  "brand": "Tesla",
  "news": {
    "keywords": "electric vehicle innovation Elon Musk"
  }
}
```
- Шукає в новинах: `"electric vehicle innovation Elon Musk"`
- Зберігає в БД як: `brand="tesla"`

---

## ⚡ Default Values

Якщо поле не передано, використовуються default значення:

| Джерело | Поле | Default |
|---------|------|---------|
| appstore | country | "us" |
| googleplay | country | "us" |
| reddit | days_back | 30 |
| reddit | sort | "new" |
| news | search_type | "everything" |
| news | language | "en" |
| global | limit | 50 |

---

## ✅ Валідація

### Обов'язкові вимоги:
1. ✅ Поле `brand` обов'язкове
2. ✅ Хоча б одне джерело має бути налаштоване
3. ✅ Якщо джерело налаштоване, його обов'язкові поля мають бути заповнені

### Помилки:
```json
// ❌ Помилка: brand відсутній
{
  "reddit": {
    "keywords": "test"
  }
}

// ❌ Помилка: жодного джерела
{
  "brand": "Test"
}

// ❌ Помилка: appstore без id
{
  "brand": "Test",
  "appstore": {
    "country": "us"
  }
}

// ✅ Правильно
{
  "brand": "Test",
  "reddit": {
    "keywords": "test keyword"
  }
}
```

---

## 📊 Відповідь

### Success (200):
```json
{
  "job_id": "job_20241005_120000_abc123de",
  "brand": "Tesla",
  "collection_results": [
    {
      "source": "appstore",
      "success": true,
      "data": {
        "success": true,
        "statistics": {
          "fetched": 50,
          "saved": 48,
          "skipped": 2
        }
      }
    },
    {
      "source": "reddit",
      "success": true,
      "data": {
        "success": true,
        "statistics": {
          "fetched": 75,
          "saved": 75,
          "skipped": 0
        }
      }
    }
  ],
  "processing_result": {
    "success": true,
    "response": {
      "message": "Data received successfully"
    }
  }
}
```

### Error (400):
```json
{
  "error": "ValidationError",
  "message": "Field 'brand' is required"
}
```

---

## 🚀 Deployment

Після внесення змін:
```bash
cd cdk
cdk deploy
```

---

**Версія:** 2.0 (Оптимізована структура)  
**Дата:** 2024-10-05

