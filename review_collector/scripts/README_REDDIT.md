# Reddit Test Script - Quick Start

## 🚀 Швидкий старт

### 1. Встановіть залежності
```bash
cd /Users/myk/PycharmProjects/monitor/VibeCodingHackathon/review_collector/scripts

# Створіть virtual environment (якщо ще не створено)
python3 -m venv venv_reddit
source venv_reddit/bin/activate

# Встановіть PRAW
pip install praw
```

### 2. Налаштуйте credentials
Ваші Reddit API credentials:
- **Client ID**: `Ao_QStxK9p0cS5875yH6Ag`
- **Client Secret**: `-Y65zQvx1EBPy9rIzUX0_TYRi5Z_Yw`

Вони вже прописані в `test_reddit.sh`

### 3. Запустіть тест
```bash
# Активуйте virtual environment
source venv_reddit/bin/activate

# Встановіть credentials
export REDDIT_CLIENT_ID="Ao_QStxK9p0cS5875yH6Ag"
export REDDIT_CLIENT_SECRET="-Y65zQvx1EBPy9rIzUX0_TYRi5Z_Yw"
export REDDIT_USER_AGENT="Brand Monitor Test Script v1.0"

# Запустіть тест
python3 test_reddit.py --brand "Tesla" --limit 20
```

## 📋 Приклади використання

```bash
# Базовий пошук
python3 test_reddit.py --brand "Tesla" --limit 50

# Топові пости за тиждень
python3 test_reddit.py --brand "Nike" --days 7 --sort top

# Зберегти результати в JSON
python3 test_reddit.py --brand "Apple" --limit 100 --save

# Тихий режим (тільки статистика)
python3 test_reddit.py --brand "Zara" --limit 20 --quiet
```

## 🎯 Що далі?

Після успішного тестування можна створити:
1. Lambda функцію для збору даних з Reddit
2. Інтеграцію з DynamoDB для збереження постів
3. Додати Reddit collector в Step Functions workflow

Детальна документація: `REDDIT_GUIDE.md`

