# Reddit API Test Results

## ✅ Тестування успішно завершено!

**Дата тестування:** 5 жовтня 2025  
**Reddit API Credentials:** Працюють коректно

---

## 🎯 Результати тестування по різних брендах

### 1. Tesla (20 постів, 30 днів)
- ✅ **Знайдено:** 10 постів
- **Score:** 92 upvotes
- **Коментарі:** 18
- **Топ subreddits:** r/F150Lightning, r/MachE, r/TeslaLounge, r/stocks
- **Середній upvote ratio:** 99.6%

### 2. Nike (15 постів, 30 днів, топові)
- ✅ **Знайдено:** 15 постів  
- **Score:** 121,461 upvotes (!)
- **Коментарі:** 6,815
- **Топ subreddits:** r/agedlikemilk, r/BlackPeopleTwitter, r/ireland
- **Середній upvote ratio:** 96.9%

### 3. Apple (5 постів, 7 днів)
- ✅ **Знайдено:** 5 постів
- **Score:** 6 upvotes
- **Коментарі:** 2
- **Середній upvote ratio:** 90.0%

### 4. Flo Health (20 постів, 30 днів)
- ✅ **Знайдено:** 6 постів
- **Score:** 109 upvotes
- **Коментарі:** 66
- **Топ subreddits:** r/degoogle, r/PrivacyHelp, r/Femtech
- **Релевантність:** Висока - пости про privacy lawsuit
- **Середній upvote ratio:** 91.5%

### 5. Flo app (30 постів, 30 днів) ⭐ НАЙКРАЩА РЕЛЕВАНТНІСТЬ
- ✅ **Знайдено:** 30 постів
- **Score:** 165 upvotes
- **Коментарі:** 222
- **Топ subreddits:** 
  - r/birthcontrol (4 пости)
  - r/amipregnant (4 пости)
  - r/Periods (3 пости)
  - r/TFABLinePorn (2 пости)
  - r/pregnant (2 пости)
- **Релевантність:** ⭐⭐⭐⭐⭐ Дуже висока!
- **Середній upvote ratio:** 83.8%

---

## 📊 Структура зібраних даних

Кожен пост містить:
```json
{
  "id": "1nxu814",
  "title": "Asking for peace of mind.",
  "text": "Full post text...",
  "author": "okbirdywirdy",
  "subreddit": "birthcontrol",
  "score": 1,
  "upvote_ratio": 1.0,
  "num_comments": 4,
  "created_utc": 1759585044.0,
  "created_date": "2025-10-04T13:37:24+00:00",
  "url": "https://www.reddit.com/...",
  "permalink": "https://www.reddit.com/r/birthcontrol/...",
  "is_self": true,
  "over_18": false,
  "brand": "Flo app",
  "age_days": 0,
  "link_flair_text": "Mistake or Risk?",
  "domain": "self.birthcontrol"
}
```

---

## 💡 Висновки

### ✅ Що працює відмінно:
1. **Reddit API підключення** - стабільне, швидке
2. **Пошук по бренду** - знаходить релевантні пости
3. **Збір даних** - повна інформація про кожен пост
4. **Фільтрація по даті** - працює коректно
5. **Різні режими сортування** - new/hot/top/relevance

### 🎯 Рекомендації для пошуку:
- **Для точного пошуку:** використовуйте повну назву бренду (наприклад, "Flo app" замість просто "Flo")
- **Для широкого охоплення:** використовуйте коротку назву
- **Сортування "new"** - для моніторингу в реальному часі
- **Сортування "top"** - для пошуку найпопулярніших згадок
- **Сортування "relevance"** - для найрелевантніших результатів

### 📈 Статистика по Flo app:
- **Активність:** Високий рівень згадок на Reddit
- **Основні теми:** 
  - Питання про використання застосунку
  - Трекінг циклу та вагітності
  - Побічні ефекти контрацептивів
  - Privacy concerns (lawsuit)
- **Тональність:** Переважно нейтральна/позитивна (користувачі довіряють додатку для трекінгу)

---

## 🚀 Наступні кроки

1. ✅ Тестовий скрипт готовий і працює
2. ⏭️ Створити Lambda функцію на базі цього коду
3. ⏭️ Додати модель для збереження в DynamoDB (аналогічно до review/news)
4. ⏭️ Створити request/response schema
5. ⏭️ Інтегрувати в Step Functions workflow
6. ⏭️ Додати в CDK stack

---

## 📁 Створені файли

1. **test_reddit.py** - Головний тестовий скрипт
2. **test_reddit.sh** - Bash wrapper для швидкого запуску
3. **REDDIT_GUIDE.md** - Детальна документація
4. **README_REDDIT.md** - Швидкий старт гайд
5. **reddit_flo_app_*.json** - Приклади збережених даних

---

## 🔐 Credentials

- **Client ID:** `Ao_QStxK9p0cS5875yH6Ag`
- **Client Secret:** `-Y65zQvx1EBPy9rIzUX0_TYRi5Z_Yw`
- **Status:** ✅ Активні, працюють

---

**Готово до створення Lambda функції! 🎉**

