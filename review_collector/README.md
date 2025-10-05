# Review Collector 🚀

Serverless система для збору **відгуків** та **новин** через SerpAPI, DataForSEO та NewsAPI.

## 🎯 Особливості

- ✅ **Збір відгуків** з App Store, Google Play, Trustpilot
- ✅ **Збір новин** 🆕 - моніторинг медіа через NewsAPI
- ✅ **Три API провайдери**: SerpAPI + DataForSEO + NewsAPI
- ✅ **HTTP API** - два незалежні endpoints
- ✅ **Ручний тригер** - скрипти для інтерактивного запуску
- ✅ **Idempotent** - відсутність дублікатів через `content_hash`
- ✅ **Serverless** - AWS Lambda + DynamoDB + API Gateway
- ✅ **Infrastructure as Code** - повний деплой через AWS CDK

---

## 🚀 Швидкий Старт

### 1. Отримати API Keys

```bash
# SerpAPI (для App Store, Google Play)
# Зареєструватись: https://serpapi.com/users/sign_up
# Free tier: 100 searches/month

# DataForSEO (для Trustpilot)
# Зареєструватись: https://dataforseo.com/
# Credentials: login + password

# NewsAPI 🆕 (для новин)
# Зареєструватись: https://newsapi.org/register
# Free tier: 100 requests/day
```

### 2. Setup

```bash
cd review_collector

# Додати API credentials в AWS Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id review-collector/credentials \
  --secret-string '{
    "serpapi": {"api_key": "YOUR_SERPAPI_KEY"},
    "dataforseo": {"login": "your@email.com", "password": "your_password"},
    "newsapi": {"api_key": "YOUR_NEWSAPI_KEY"}
  }'

# Встановити CDK залежності
cd cdk
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Deploy
cdk deploy
```

### 3. Збирати дані!

#### 📱 Відгуки (Reviews)

```bash
# HTTP API
curl -X POST "https://YOUR_API_URL/collect-reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 50
  }'
```

#### 🗞️ Новини (News) 🆕

```bash
# HTTP API
curl -X POST "https://YOUR_API_URL/collect-news" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Tesla",
    "limit": 50,
    "search_type": "everything",
    "language": "en"
  }'
```

---

## 📖 Повна Документація

### Reviews Collection
➡️ **[API_INSTRUCTIONS.md](./API_INSTRUCTIONS.md)** - Інструкція користувача API  
➡️ **[SERPAPI_GUIDE.md](./SERPAPI_GUIDE.md)** - Гайд по SerpAPI (App Store, Google Play)  
➡️ **[DATAFORSEO_GUIDE.md](./DATAFORSEO_GUIDE.md)** - Гайд по DataForSEO (Trustpilot)  

### News Collection 🆕
➡️ **[NEWSAPI_GUIDE.md](./NEWSAPI_GUIDE.md)** - Гайд по NewsAPI (новини)  

### Infrastructure
➡️ **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Інструкція деплою  
➡️ **[DATABASE_ACCESS.md](./DATABASE_ACCESS.md)** - Доступ до даних у DynamoDB

---

## 🏗️ Архітектура

```
┌──────────────────────────────────────────────────┐
│              API Gateway                          │
├─────────────────────┬────────────────────────────┤
│  /collect-reviews   │  /collect-news 🆕          │
└──────────┬──────────┴────────────┬───────────────┘
           ▼                       ▼
  ┌──────────────────┐    ┌──────────────────┐
  │ Review Lambda    │    │ News Lambda 🆕   │
  │ (SerpAPI +       │    │ (NewsAPI)        │
  │  DataForSEO)     │    │                  │
  └────────┬─────────┘    └────────┬─────────┘
           │                       │
           └───────────┬───────────┘
                       ▼
              ┌─────────────────┐
              │   DynamoDB      │
              │ ReviewsTableV2  │
              │                 │
              │ - Reviews (pk)  │
              │ - News (news#)  │
              └─────────────────┘
```

---

## 📦 Структура Проекту

```
review_collector/
├── src/
│   ├── serpapi_collector/        # Reviews collector
│   │   ├── handler.py            # Lambda entry point
│   │   ├── serpapi_base_client.py
│   │   ├── serpapi_appstore_client.py
│   │   ├── serpapi_googleplay_client.py
│   │   └── requirements.txt
│   │
│   ├── news_collector/           # 🆕 News collector
│   │   ├── handler.py            # Lambda entry point
│   │   ├── newsapi_client.py     # NewsAPI integration
│   │   ├── news_article.py       # Domain entity
│   │   ├── news_repository.py    # DynamoDB adapter
│   │   ├── collect_news_use_case.py
│   │   └── requirements.txt
│   │
│   └── shared/                   # Shared infrastructure
│       ├── domain/               # Domain entities
│       ├── application/          # Use cases
│       └── infrastructure/       # DynamoDB, Secrets
│
├── cdk/                          # Infrastructure as Code
│   ├── app.py
│   ├── stacks/
│   │   └── review_collector_stack.py
│   └── requirements.txt
│
├── scripts/                      # Manual trigger scripts
│   ├── collect_reviews.sh        # Bash interactive menu
│   └── manual_trigger.py         # Python CLI
│
├── SERPAPI_GUIDE.md             # 📚 Повний гайд
└── README.md                    # Цей файл
```

---

## 🎮 Приклади Використання

### App Store Reviews

```bash
# Telegram
python scripts/manual_trigger.py --source appstore --app-id 544007664 --brand telegram

# WhatsApp
python scripts/manual_trigger.py --source appstore --app-id 310633997 --brand whatsapp

# Instagram
python scripts/manual_trigger.py --source appstore --app-id 389801252 --brand instagram
```

### Google Play Reviews

```bash
# Telegram
python scripts/manual_trigger.py --source googleplay --app-id org.telegram.messenger --brand telegram

# WhatsApp
python scripts/manual_trigger.py --source googleplay --app-id com.whatsapp --brand whatsapp
```

### Trustpilot Reviews

```bash
# Tesla
python scripts/manual_trigger.py --source trustpilot --app-id tesla.com --brand tesla

# Amazon
python scripts/manual_trigger.py --source trustpilot --app-id amazon.com --brand amazon
```

---

## 📊 API Response

```json
{
  "success": true,
  "message": "Reviews collected successfully",
  "statistics": {
    "fetched": 50,
    "saved": 48,
    "skipped": 2,
    "errors": 0,
    "duration_seconds": 5.3
  },
  "input": {
    "source": "appstore",
    "app_identifier": "544007664",
    "brand": "telegram",
    "limit": 50
  }
}
```

---

## 💰 Вартість

| Компонент | Вартість |
|-----------|----------|
| AWS (Lambda, DynamoDB, API Gateway) | ~$0.70/міс |
| SerpAPI Free tier | $0 (100 searches/міс) |
| SerpAPI Basic | $50/міс (5,000 searches) |
| **Total (Free tier)** | **$0.70/міс** |
| **Total (Basic)** | **$50.70/міс** |

---

## 🔧 Що Змінилось?

### Старе Рішення ❌
- 3 окремі Lambda functions (appstore, googleplay, trustpilot)
- Hardcoded `APP_IDENTIFIER` в env vars
- Потрібні окремі API credentials для кожної платформи
- Тільки scheduled збір (EventBridge)
- Тільки свої додатки

### Нове Рішення ✅
- 1 unified Lambda function
- Dynamic `app_identifier` в request
- Один SerpAPI key
- On-demand збір через HTTP API
- **Будь-які публічні додатки!**

---

## 🛠️ Розробка

### Локальне тестування

```bash
# Set environment
export TABLE_NAME=ReviewsTable
export SECRET_NAME=review-collector/credentials

# Run handler
cd src/serpapi_collector
python -c "from handler import handler; handler({'source':'appstore','app_identifier':'544007664','brand':'test'}, None)"
```

### CDK Commands

```bash
cd cdk

# Synth CloudFormation
cdk synth

# Diff changes
cdk diff

# Deploy
cdk deploy

# Destroy
cdk destroy
```

---

## 📚 Документація

- **[SERPAPI_GUIDE.md](./SERPAPI_GUIDE.md)** - Повний гайд з прикладами
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment інструкції (старе рішення)
- **[PLAN.md](./PLAN.md)** - Початковий план проекту

---

## 🔗 Корисні Посилання

- [SerpAPI Documentation](https://serpapi.com/docs)
- [SerpAPI App Store API](https://serpapi.com/apple-app-store)
- [SerpAPI Google Play API](https://serpapi.com/google-play)
- [SerpAPI Trustpilot API](https://serpapi.com/trustpilot)

---

## 🤝 Use Cases

### 1. Competitor Analysis 🔍
Збирайте та аналізуйте відгуки конкурентів для покращення свого продукту.

### 2. Market Research 📊
Досліджуйте настрої користувачів різних додатків у вашій ніші.

### 3. Sentiment Analysis 💭
Використовуйте зібрані відгуки для аналізу sentiment за допомогою ML моделей.

### 4. Review Monitoring 📱
Автоматично відслідковуйте нові відгуки на свої та конкурентні додатки.

---

## 🐛 Troubleshooting

**Problem:** Lambda timeout  
**Solution:** Збільшити timeout в CDK stack до 10 хвилин

**Problem:** SerpAPI rate limit  
**Solution:** Зачекати 1-2 хвилини або оновити план

**Problem:** Invalid app_identifier  
**Solution:** Перевірити формат (App Store: числовий ID, Google Play: package name)

Більше у [SERPAPI_GUIDE.md](./SERPAPI_GUIDE.md#troubleshooting)

---

## 📄 License

MIT License

---

**Built with ❤️ using SerpAPI, AWS CDK, and Python 3.11**
