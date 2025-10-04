# Review Collector API - Інструкція користувача

## 🎯 Що це таке?

Review Collector API - це сервіс для автоматичного збору відгуків з App Store, Google Play та Trustpilot. API збирає, нормалізує та зберігає відгуки в єдиному форматі для подальшого аналізу.

---

## 📡 Базова інформація

### Endpoint
```
POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews
```

### Регіон
```
us-east-1 (N. Virginia)
```

### Формат
```
Content-Type: application/json
```

### Метод
```
POST
```

---

## 🚀 Швидкий старт

### Крок 1: Підготуйте дані

Вам потрібно знати:
1. **Платформу** - де знаходиться ваш додаток/бізнес
2. **Ідентифікатор** - унікальний ID додатка на платформі
3. **Бренд** - назва вашого бренду/компанії

### Крок 2: Знайдіть ідентифікатор додатка

#### App Store
1. Відкрийте додаток в App Store
2. URL виглядає так: `https://apps.apple.com/us/app/telegram-messenger/id544007664`
3. Ідентифікатор: `544007664` (тільки цифри після `id`)

#### Google Play
1. Відкрийте додаток в Google Play
2. URL виглядає так: `https://play.google.com/store/apps/details?id=org.telegram.messenger`
3. Ідентифікатор: `org.telegram.messenger` (значення параметра `id`)

#### Trustpilot
1. Відкрийте сторінку компанії на Trustpilot
2. URL виглядає так: `https://www.trustpilot.com/review/telegram.org`
3. Ідентифікатор: `telegram.org` (домен після `/review/`)

### Крок 3: Зробіть запит

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

## 📋 Параметри запиту

### Обов'язкові параметри

| Параметр | Тип | Опис | Приклад |
|----------|-----|------|---------|
| `source` | string | Платформа: `appstore`, `googleplay`, або `trustpilot` | `"appstore"` |
| `app_identifier` | string | Ідентифікатор додатка (формат залежить від платформи) | `"544007664"` |
| `brand` | string | Назва бренду (для фільтрації та групування) | `"telegram"` |

### Опціональні параметри

| Параметр | Тип | За замовчуванням | Опис |
|----------|-----|------------------|------|
| `limit` | integer | `100` | Максимальна кількість відгуків (1-500) |
| `country` | string | `"us"` | Код країни (ISO 3166-1 alpha-2) |
| `metadata` | object | `{}` | Додаткові дані для трекінгу |

---

## 💡 Приклади використання

### Приклад 1: Базовий запит (App Store)

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram"
  }'
```

**Результат:**
```json
{
  "success": true,
  "message": "Reviews collected successfully",
  "statistics": {
    "brand": "telegram",
    "app_identifier": "544007664",
    "fetched": 100,
    "saved": 95,
    "skipped": 5,
    "errors": 0,
    "duration_seconds": 12.5
  }
}
```

### Приклад 2: Google Play з лімітом

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "googleplay",
    "app_identifier": "org.telegram.messenger",
    "brand": "telegram",
    "limit": 50
  }'
```

### Приклад 3: З вказанням країни

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100,
    "country": "gb"
  }'
```

### Приклад 4: З metadata для трекінгу

```bash
curl -X POST https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews \
  -H "Content-Type: application/json" \
  -d '{
    "source": "googleplay",
    "app_identifier": "org.telegram.messenger",
    "brand": "telegram",
    "limit": 100,
    "metadata": {
      "campaign": "monthly_monitoring",
      "requester": "analytics_team",
      "date": "2024-10-04"
    }
  }'
```

---

## 📊 Формат відповіді

### Успішна відповідь (HTTP 200)

```json
{
  "success": true,
  "message": "Reviews collected successfully",
  "statistics": {
    "brand": "telegram",
    "app_identifier": "544007664",
    "fetched": 100,          // Скільки відгуків отримано з API
    "saved": 95,             // Скільки нових відгуків збережено
    "skipped": 5,            // Скільки дублікатів пропущено
    "errors": 0,             // Скільки помилок при обробці
    "start_time": "2024-10-04T14:30:00",
    "end_time": "2024-10-04T14:30:12.5",
    "duration_seconds": 12.5
  },
  "request": {
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 100,
    "country": "us",
    "metadata": {}
  }
}
```

### Помилка валідації (HTTP 400)

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid source: 'xxx'. Must be one of: appstore, googleplay, trustpilot",
  "request": {...}
}
```

### Серверна помилка (HTTP 500)

```json
{
  "success": false,
  "error": "InternalServerError",
  "message": "Failed to connect to SerpAPI",
  "request": {...}
}
```

---

## 🔧 Інтеграція в код

### Python

```python
import requests

def collect_reviews(source, app_identifier, brand, limit=100):
    """Збір відгуків через API"""
    url = "https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews"
    
    payload = {
        "source": source,
        "app_identifier": app_identifier,
        "brand": brand,
        "limit": limit
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            stats = data["statistics"]
            print(f"✅ Успішно: {stats['fetched']} отримано, {stats['saved']} збережено")
            return stats
        else:
            print(f"❌ Помилка: {data['message']}")
            return None
    else:
        print(f"❌ HTTP {response.status_code}: {response.text}")
        return None

# Використання
stats = collect_reviews(
    source="appstore",
    app_identifier="544007664",
    brand="telegram",
    limit=100
)
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function collectReviews(source, appIdentifier, brand, limit = 100) {
  const url = 'https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews';
  
  try {
    const response = await axios.post(url, {
      source,
      app_identifier: appIdentifier,
      brand,
      limit
    });
    
    if (response.data.success) {
      const stats = response.data.statistics;
      console.log(`✅ Успішно: ${stats.fetched} отримано, ${stats.saved} збережено`);
      return stats;
    } else {
      console.log(`❌ Помилка: ${response.data.message}`);
      return null;
    }
  } catch (error) {
    console.error('❌ Помилка:', error.message);
    return null;
  }
}

// Використання
collectReviews('appstore', '544007664', 'telegram', 100);
```

### PHP

```php
<?php

function collectReviews($source, $appIdentifier, $brand, $limit = 100) {
    $url = 'https://xp9v1vxlih.execute-api.us-east-1.amazonaws.com/prod/collect-reviews';
    
    $data = [
        'source' => $source,
        'app_identifier' => $appIdentifier,
        'brand' => $brand,
        'limit' => $limit
    ];
    
    $options = [
        'http' => [
            'header'  => "Content-Type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($data)
        ]
    ];
    
    $context = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    $response = json_decode($result, true);
    
    if ($response['success']) {
        $stats = $response['statistics'];
        echo "✅ Успішно: {$stats['fetched']} отримано, {$stats['saved']} збережено\n";
        return $stats;
    } else {
        echo "❌ Помилка: {$response['message']}\n";
        return null;
    }
}

// Використання
collectReviews('appstore', '544007664', 'telegram', 100);
?>
```

---

## ⚠️ Важливі обмеження

### Ліміти по платформах

| Платформа | Відгуків на сторінку | Рекомендований max limit | Пагінація |
|-----------|----------------------|--------------------------|-----------|
| App Store | ~25 | 200 | ✅ Так |
| Google Play | ~20 | 200 | ✅ Так |
| Trustpilot | 20 | 20 | ❌ Ні (тільки 1 сторінка) |

### Час виконання

- **Середній час**: 1-15 секунд залежно від кількості відгуків
- **Timeout**: 120 секунд (Lambda timeout)
- **Рекомендація**: Для збору великої кількості відгуків (>200) робіть декілька запитів

### Дедуплікація

- API автоматично визначає дублікати за `content_hash`
- Дублікати не зберігаються повторно
- Безпечно робити повторні запити

---

## 🎯 Кращі практики

### 1. Обробка помилок

```python
def collect_with_retry(source, app_id, brand, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = collect_reviews(source, app_id, brand)
            if result:
                return result
        except Exception as e:
            print(f"Спроба {attempt + 1} не вдалася: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None
```

### 2. Батчова обробка

```python
apps = [
    ("appstore", "544007664", "telegram"),
    ("googleplay", "org.telegram.messenger", "telegram"),
    ("appstore", "310633997", "whatsapp"),
]

for source, app_id, brand in apps:
    print(f"\n📱 Збір відгуків: {brand} ({source})")
    stats = collect_reviews(source, app_id, brand, limit=50)
    time.sleep(1)  # Пауза між запитами
```

### 3. Моніторинг результатів

```python
def monitor_collection(stats):
    if stats['errors'] > 0:
        print(f"⚠️ Увага: {stats['errors']} помилок при обробці")
    
    if stats['saved'] == 0 and stats['fetched'] > 0:
        print("ℹ️ Всі відгуки вже були зібрані раніше")
    
    efficiency = stats['saved'] / stats['fetched'] * 100 if stats['fetched'] > 0 else 0
    print(f"📊 Ефективність: {efficiency:.1f}% нових відгуків")
```

---

## 📞 Підтримка

### Типові помилки

#### "Invalid source"
```
Помилка: Невірне значення source
Рішення: Використовуйте "appstore", "googleplay" або "trustpilot"
```

#### "app_identifier must be a non-empty string"
```
Помилка: Відсутній або пустий app_identifier
Рішення: Перевірте, що ви передали правильний ID додатка
```

#### "limit must be an integer between 1 and 500"
```
Помилка: Невірне значення limit
Рішення: Використовуйте число від 1 до 500
```

### Логи

Для дебагу можна переглянути логи Lambda функції в CloudWatch:
```
AWS Console → CloudWatch → Log Groups → /aws/lambda/serpapi-collector-lambda
```

---

## 📚 Додаткові ресурси

- **Детальні приклади**: [REQUEST_EXAMPLES.md](REQUEST_EXAMPLES.md)
- **Швидкий довідник**: [API_SCHEMA.md](API_SCHEMA.md)
- **База даних**: [DATABASE_ACCESS.md](DATABASE_ACCESS.md)

---

## ✅ Чеклист готовності

Перед використанням API перевірте:

- [ ] У вас є правильний `app_identifier` для кожної платформи
- [ ] Ви знаєте назву вашого бренду
- [ ] Ви розумієте обмеження по кількості відгуків
- [ ] У вас налаштована обробка помилок
- [ ] Ви готові обробляти відповіді API

---

**Версія API**: 1.0  
**Останнє оновлення**: 4 жовтня 2024  
**Регіон**: us-east-1  
**Статус**: ✅ Працює

