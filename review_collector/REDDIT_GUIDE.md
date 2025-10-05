# Reddit API Integration Guide

Гайд по інтеграції з Reddit API для збору постів з згадками бренду.

## 📋 Зміст

1. [Створення Reddit App](#створення-reddit-app)
2. [Тестування API](#тестування-api)
3. [Структура даних](#структура-даних)
4. [Lambda функція](#lambda-функція)

---

## 🔧 Створення Reddit App

### Крок 1: Реєстрація додатку

1. Відкрийте: https://www.reddit.com/prefs/apps
2. Натисніть **"create app"** або **"create another app"**
3. Заповніть форму:
   - **name**: Brand Monitor (або будь-яка назва)
   - **App type**: Виберіть **"script"**
   - **description**: Brand monitoring tool (опціонально)
   - **about url**: залиште порожнім
   - **redirect uri**: `http://localhost:8080`
4. Натисніть **"create app"**

### Крок 2: Отримання credentials

Після створення додатку ви побачите:
- **client_id**: Знаходиться під назвою додатку (короткий рядок)
- **client_secret**: Знаходиться в полі "secret"

Збережіть ці дані!

---

## 🧪 Тестування API

### Встановлення залежностей

```bash
pip install praw
```

### Налаштування credentials

**Варіант 1: Environment variables**
```bash
export REDDIT_CLIENT_ID="ваш_client_id"
export REDDIT_CLIENT_SECRET="ваш_client_secret"
export REDDIT_USER_AGENT="Brand Monitor v1.0"
```

**Варіант 2: Редагувати test_reddit.sh**
```bash
cd VibeCodingHackathon/review_collector/scripts
nano test_reddit.sh  # Вставте свої credentials
```

### Запуск тестів

**Базовий тест:**
```bash
cd VibeCodingHackathon/review_collector/scripts
python3 test_reddit.py --brand "Tesla" --limit 20
```

**Параметри:**
- `--brand`: Назва бренду для пошуку (обов'язково)
- `--limit`: Максимальна кількість постів (default: 50)
- `--days`: Скільки днів назад шукати (default: 30)
- `--sort`: Порядок сортування (new/hot/relevance/top, default: new)
- `--save`: Зберегти результати в JSON файл
- `--quiet`: Показати лише summary

**Приклади:**

```bash
# Пошук згадок Tesla за останній місяць
python3 test_reddit.py --brand "Tesla" --limit 50 --days 30

# Пошук топових постів про Apple за тиждень
python3 test_reddit.py --brand "Apple" --days 7 --sort top

# Зберегти результати в JSON
python3 test_reddit.py --brand "Nike" --limit 100 --save

# Тихий режим (лише статистика)
python3 test_reddit.py --brand "Zara" --limit 20 --quiet
```

**Запуск всіх тестів:**
```bash
chmod +x test_reddit.sh
./test_reddit.sh
```

---

## 📊 Структура даних

Кожен пост містить наступні поля:

```json
{
  "id": "abc123",
  "title": "Just bought a Tesla Model 3!",
  "text": "Full text of the post body...",
  "author": "username",
  "subreddit": "teslamotors",
  "score": 342,
  "upvote_ratio": 0.95,
  "num_comments": 87,
  "created_utc": 1728000000,
  "created_date": "2025-10-04T12:00:00",
  "url": "https://example.com/link",
  "permalink": "https://www.reddit.com/r/teslamotors/comments/...",
  "is_self": true,
  "over_18": false,
  "spoiler": false,
  "stickied": false,
  "locked": false,
  "brand": "Tesla",
  "age_days": 3,
  "link_flair_text": "Discussion",
  "domain": "self.teslamotors"
}
```

### Типи постів

**Text post** (`is_self: true`):
- Має текст в полі `text`
- `domain` буде `self.subreddit_name`
- `url` веде на Reddit

**Link post** (`is_self: false`):
- Поле `text` порожнє
- `url` веде на зовнішній сайт
- `domain` показує домен посилання

---

## 🎯 Що показує скрипт

### Summary Statistics
- Загальна кількість знайдених постів
- Сумарний score (upvotes)
- Загальна кількість коментарів
- Середній upvote ratio
- Кількість унікальних subreddits
- Топ-5 subreddits з найбільшою кількістю згадок

### Детальна інформація по постах
- Заголовок
- Автор
- Subreddit
- Посилання
- Дата створення
- Score, upvote ratio, кількість коментарів
- Тип поста (текст або посилання)
- Превью тексту

---

## 💡 Поради

### Пошук

1. **Точний пошук**: Скрипт використовує лапки для точного пошуку фрази
   ```python
   search_query = f'"{brand}"'  # Шукає точну фразу
   ```

2. **Time filter**: Reddit має вбудований фільтр по часу (month/week/day/year/all)

3. **Sorting options**:
   - `new`: Нові пости (за замовчуванням)
   - `hot`: Гарячі/трендові
   - `top`: Топові за кількістю upvotes
   - `relevance`: За релевантністю

### Обмеження Reddit API

- **Rate limits**: 60 запитів на хвилину
- **Search results**: Максимум ~1000 результатів
- **Read-only**: Скрипт використовує read-only режим
- **Authentication**: Не потрібен login/password, лише app credentials

### Фільтрація

Скрипт автоматично фільтрує:
- Пости за межами вказаного періоду
- Видалені пости позначаються як `[deleted]`

---

## 🚀 Наступні кроки

1. ✅ Протестуйте скрипт з вашими credentials
2. ⏭️ Перевірте, що дані збираються коректно
3. ⏭️ Створіть Lambda функцію на базі цього коду
4. ⏭️ Додайте збереження в DynamoDB
5. ⏭️ Інтегруйте в Step Functions workflow

---

## ❓ Troubleshooting

### Помилка: "PRAW not installed"
```bash
pip install praw
```

### Помилка: "Invalid credentials"
Перевірте:
- Client ID скопійовано правильно (без пробілів)
- Client Secret скопійовано правильно
- Додаток має тип "script"

### Помилка: "401 Unauthorized"
- Перевірте user_agent (має бути унікальним)
- Переконайтесь, що credentials не прострочені

### Мало результатів
- Збільште `--limit`
- Спробуйте різні варіанти `--sort`
- Збільште `--days` для більшого періоду
- Перевірте правильність написання бренду

---

## 📚 Додаткові ресурси

- [PRAW Documentation](https://praw.readthedocs.io/)
- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [Reddit Apps Page](https://www.reddit.com/prefs/apps)

