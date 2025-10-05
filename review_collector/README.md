# Review Collector - Serverless Multi-Source Data Collection System

Serverless система для збору відгуків та новин з різних джерел (App Store, Google Play, Trustpilot, Reddit, News API) з використанням AWS Lambda, Step Functions та DynamoDB.

## 🏗️ Архітектура

### Tech Stack
- **AWS CDK** - Infrastructure as Code (Python)
- **AWS Lambda** - Serverless compute
- **AWS Step Functions** - Orchestration
- **AWS API Gateway** - REST API
- **AWS DynamoDB** - NoSQL database
- **AWS Secrets Manager** - API keys storage
- **Python 3.11** - Runtime

### Компоненти

```
┌─────────────────────────────────────────────────────────────┐
│  API Gateway                                                 │
│  POST /generate-report                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step Functions State Machine                                │
│  - Orchestrates parallel data collection                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌──────────────────┬──────────────────┐
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ App Store    │  │ Google Play  │  │ Trustpilot   │
│ Lambda       │  │ Lambda       │  │ Lambda       │
└──────────────┘  └──────────────┘  └──────────────┘
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐
│ Reddit       │  │ News API     │
│ Lambda       │  │ Lambda       │
└──────────────┘  └──────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│  DynamoDB (ReviewsTableV2)                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment

### Prerequisites
```bash
# Встановіть AWS CLI
brew install awscli  # macOS
# or
pip install awscli

# Налаштуйте AWS credentials
aws configure --profile hackathon

# Встановіть AWS CDK
npm install -g aws-cdk
```

### Deploy
```bash
cd cdk

# Створіть virtual environment
python3 -m venv venv
source venv/bin/activate

# Встановіть залежності
pip install -r requirements.txt

# Bootstrap CDK (перший раз)
cdk bootstrap --profile hackathon

# Deploy stack
cdk deploy --profile hackathon
```

### Secrets Setup
Перед deployment створіть secrets в AWS Secrets Manager:

```bash
# SerpAPI key (для App Store, Google Play, Trustpilot)
aws secretsmanager create-secret \
  --profile hackathon \
  --name serpapi-key \
  --secret-string "your-serpapi-key"

# NewsAPI key
aws secretsmanager create-secret \
  --profile hackathon \
  --name newsapi-key \
  --secret-string "your-newsapi-key"

# Reddit credentials
aws secretsmanager create-secret \
  --profile hackathon \
  --name reddit-credentials \
  --secret-string '{
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "user_agent": "your-user-agent"
  }'

# DataForSEO credentials (для Trustpilot)
aws secretsmanager create-secret \
  --profile hackathon \
  --name dataforseo-credentials \
  --secret-string '{
    "username": "your-username",
    "password": "your-password"
  }'
```

## 📋 API Usage

### Endpoint
```
POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/generate-report
```

### Request Format

```json
{
  "brand": "Tesla",
  "appstore": {
    "id": "123456789",
    "country": "us"
  },
  "googleplay": {
    "package_name": "com.example.app",
    "country": "us"
  },
  "trustpilot": {
    "domain": "tesla.com"
  },
  "reddit": {
    "keywords": "Tesla Model 3",
    "days_back": 30,
    "sort": "new"
  },
  "news": {
    "keywords": "Tesla electric vehicle",
    "search_type": "everything",
    "from_date": "2024-10-01",
    "to_date": "2024-10-05",
    "language": "en"
  },
  "limit": 50,
  "processing_endpoint_url": "https://your-webhook.com/process"
}
```

### Мінімальний запит

Всі поля опціональні, крім `brand` та мінімум одного джерела:

```json
{
  "brand": "Tesla",
  "reddit": {
    "keywords": "Tesla"
  },
  "news": {
    "keywords": "Tesla"
  }
}
```

### Default Values

| Поле | Default |
|------|---------|
| `limit` | 50 |
| `appstore.country` | "us" |
| `googleplay.country` | "us" |
| `reddit.days_back` | 30 |
| `reddit.sort` | "new" |
| `news.search_type` | "everything" |
| `news.language` | "en" |

## 📊 Response

```json
{
  "message": "Report generation started",
  "executionArn": "arn:aws:states:...:execution:...",
  "startDate": "1.759624067676E9"
}
```

Для перевірки статусу:
```bash
aws stepfunctions describe-execution \
  --profile hackathon \
  --execution-arn "arn:aws:states:..." \
  --query 'status'
```

## 🧪 Testing

### Тестовий запит
```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Telegram",
    "appstore": {"id": "686449807"},
    "googleplay": {"package_name": "org.telegram.messenger"},
    "trustpilot": {"domain": "telegram.org"},
    "reddit": {"keywords": "telegram app"},
    "news": {"keywords": "Telegram"},
    "limit": 10
  }'
```

### Перегляд результатів у DynamoDB

```bash
# Отримати всі записи для бренду
aws dynamodb query \
  --profile hackathon \
  --table-name ReviewsTableV2 \
  --key-condition-expression "brand = :brand" \
  --expression-attribute-values '{":brand": {"S": "telegram"}}'

# Отримати записи з конкретного job
aws dynamodb query \
  --profile hackathon \
  --table-name ReviewsTableV2 \
  --index-name job_id-index \
  --key-condition-expression "job_id = :jobid" \
  --expression-attribute-values '{":jobid": {"S": "job_20241005_123456_abc"}}'
```

## 📁 Project Structure

```
review_collector/
├── cdk/                          # AWS CDK infrastructure code
│   ├── app.py                    # CDK app entry point
│   ├── stacks/
│   │   └── review_collector_stack.py  # Main stack definition
│   └── requirements.txt
├── src/
│   ├── shared/                   # Shared code (Lambda Layer)
│   │   ├── domain/               # Domain models
│   │   ├── application/          # Use cases
│   │   ├── infrastructure/       # Repositories & clients
│   │   └── utils/                # Utilities
│   ├── report_initializer/       # Report initialization Lambda
│   ├── serpapi_collector/        # App Store/Play/Trustpilot Lambda
│   ├── reddit_collector/         # Reddit Lambda
│   ├── news_collector/           # News API Lambda
│   └── http_caller/              # HTTP webhook caller Lambda
├── examples/                     # Usage examples
└── scripts/                      # Helper scripts
```

## 🔑 API Keys Required

1. **SerpAPI** - https://serpapi.com
   - Used for: App Store, Google Play
   
2. **DataForSEO** - https://dataforseo.com
   - Used for: Trustpilot
   
3. **NewsAPI** - https://newsapi.org
   - Used for: News articles
   
4. **Reddit API** - https://www.reddit.com/prefs/apps
   - Used for: Reddit posts

## 🛠️ Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Linting
flake8 src/
mypy src/
```

### Update Lambda

```bash
cd cdk
cdk deploy --profile hackathon
```

## 📚 Documentation

- `OPTIMIZED_STRUCTURE_EXAMPLES.md` - Детальні приклади API запитів
- `DEPLOYMENT.md` - Повна інструкція з deployment
- `API_SCHEMA.md` - API schema документація

## 🔍 Monitoring

Логи Lambda функцій доступні в CloudWatch:
```bash
# Переглянути логи
aws logs tail /aws/lambda/serpapi-collector-lambda --profile hackathon --follow
aws logs tail /aws/lambda/news-collector-lambda --profile hackathon --follow
aws logs tail /aws/lambda/reddit-collector-lambda --profile hackathon --follow
```

Step Functions execution history:
```bash
aws stepfunctions list-executions \
  --profile hackathon \
  --state-machine-arn "arn:aws:states:us-east-1:...:stateMachine:ReviewCollectorStateMachine"
```

## 📈 Scaling

- **Lambda**: Auto-scales based on load
- **DynamoDB**: On-demand billing mode
- **API Gateway**: Throttling configured
- **Step Functions**: 25,000 state transitions per second

## 💰 Costs

Приблизна вартість (low traffic):
- Lambda: $0-5/month
- DynamoDB: $0-10/month
- Step Functions: $0-2/month
- API Gateway: $0-3/month
- **Total: ~$5-20/month**

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 👥 Authors

- Mykyta - Initial work

## 🙏 Acknowledgments

- AWS CDK Documentation
- SerpAPI, NewsAPI, Reddit API, DataForSEO

