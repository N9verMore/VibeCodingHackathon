# Review Collector - Implementation Plan

## 🎯 Мета
Serverless система для збору відгуків з App Store, Google Play та Trustpilot з гарантією відсутності дублікатів.

---

## 📋 Етапи імплементації

### ✅ Phase 1: Domain Layer (Core)
- [ ] `src/shared/domain/review.py` - Review entity з валідацією та content_hash
- [ ] `src/shared/domain/review_repository.py` - Port (interface)

### ✅ Phase 2: Infrastructure Layer (Adapters)
- [ ] `src/shared/infrastructure/repositories/dynamodb_review_repository.py` - DynamoDB adapter
- [ ] `src/shared/infrastructure/clients/secrets_client.py` - AWS Secrets Manager client
- [ ] `src/shared/infrastructure/clients/base_api_client.py` - Base HTTP client

### ✅ Phase 3: Application Layer (Use Cases)
- [ ] `src/shared/application/collect_reviews_use_case.py` - Orchestration logic

### ✅ Phase 4: API Clients (Source-specific)
- [ ] `src/appstore_collector/appstore_api_client.py` - App Store Connect API
- [ ] `src/googleplay_collector/googleplay_api_client.py` - Google Play API
- [ ] `src/trustpilot_collector/trustpilot_api_client.py` - Trustpilot API

### ✅ Phase 5: Lambda Handlers
- [ ] `src/appstore_collector/handler.py` + requirements.txt
- [ ] `src/googleplay_collector/handler.py` + requirements.txt
- [ ] `src/trustpilot_collector/handler.py` + requirements.txt

### ✅ Phase 6: CDK Infrastructure
- [ ] `cdk/app.py` - Entry point
- [ ] `cdk/stacks/review_collector_stack.py` - Main stack
  - DynamoDB Table
  - 3x Lambda Functions
  - 3x EventBridge Schedulers
  - Secrets Manager
  - IAM Roles & Policies
- [ ] `cdk/cdk.json` - CDK config
- [ ] `cdk/requirements.txt` - CDK dependencies

### ✅ Phase 7: Documentation & Configuration
- [ ] `README.md` - Setup instructions
- [ ] `.gitignore` - Python & CDK
- [ ] `requirements-dev.txt` - Dev dependencies

---

## 🏗️ Архітектура

### Hexagonal (Ports & Adapters)
```
┌─────────────────────────────────────────────────┐
│               Lambda Handler                     │
│         (appstore/googleplay/trustpilot)        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Application Layer (Use Case)            │
│      CollectReviewsUseCase.execute()            │
└────┬─────────────────────────────────────┬──────┘
     │                                     │
     ▼                                     ▼
┌──────────────────┐           ┌──────────────────┐
│  Domain Layer    │           │ Infrastructure   │
│  - Review        │◄──────────┤  - API Clients   │
│  - Repository    │           │  - DynamoDB      │
│    (Port)        │           │  - Secrets Mgr   │
└──────────────────┘           └──────────────────┘
```

### AWS Resources
- **DynamoDB**: ReviewsTable (PK: `source#id`, GSI: `brand-created_at-index`)
- **Lambda** x3: 512MB, Python 3.12, 5min timeout
- **EventBridge**: Cron `0 2 * * ? *` (2 AM UTC daily)
- **Secrets Manager**: API credentials

---

## 📦 Data Model

```python
Review:
  id: str                    # Source review ID
  source: str                # "appstore" | "googleplay" | "trustpilot"
  backlink: str              # URL to review
  brand: str                 # Brand identifier
  app_identifier: str        # bundleId / packageName / businessUnitId
  title: Optional[str]       # Review title
  text: Optional[str]        # Review text
  rating: int                # 1-5
  language: str              # ISO language code
  country: Optional[str]     # ISO country code
  author_hint: Optional[str] # Username (no PII)
  created_at: datetime       # Review creation time
  fetched_at: datetime       # Collection timestamp
  content_hash: str          # SHA256 of stable fields
```

---

## 🔄 Flow

```
EventBridge Scheduler (daily 2 AM)
    ↓
Lambda Handler
    ↓
CollectReviewsUseCase
    ├─→ Get credentials from Secrets Manager
    ├─→ Fetch reviews from API (with pagination)
    ├─→ Normalize to Review entities
    └─→ Save to DynamoDB (idempotent upsert)
```

---

## 🛡️ Idempotency Strategy

```python
PK = f"{source}#{id}"
existing = dynamodb.get_item(Key=PK)

if existing and existing.content_hash == new_review.content_hash:
    skip  # No changes
else:
    dynamodb.put_item(new_review)  # Create or update
```

---

## 🚀 Deployment

```bash
cd review_collector/cdk
pip install -r requirements.txt
cdk bootstrap  # First time only
cdk deploy
```

---

## 📚 Dependencies

### CDK
- `aws-cdk-lib==2.100.0`
- `constructs>=10.0.0`

### Lambda
- `boto3` - AWS SDK
- `requests` - HTTP client
- `pyjwt` - JWT for App Store
- `cryptography` - Key handling
- `google-auth` - Google OAuth

---

## 🎯 SOLID Principles Applied

- **S**: Each API client handles one source
- **O**: New sources = new adapters, no core changes
- **L**: All API clients extend BaseAPIClient
- **I**: ReviewRepository has minimal interface
- **D**: Use cases depend on ports, not concrete implementations

---

## 📊 Success Criteria

- [ ] All 3 sources collecting reviews daily
- [ ] No duplicate reviews in DynamoDB
- [ ] Idempotent re-runs (same reviews = no DB writes)
- [ ] CloudWatch logs for debugging
- [ ] Deployment via CDK in < 5 minutes

