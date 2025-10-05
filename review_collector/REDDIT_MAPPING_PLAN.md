# Reddit Posts → Review Entity Mapping Plan

План маппінгу даних з Reddit постів до стандартної структури `Review`, яка використовується для App Store, Google Play та Trustpilot.

---

## 📊 Існуюча структура Review Entity

```python
@dataclass
class Review:
    # Required fields
    id: str                    # Unique review ID
    source: ReviewSource       # Platform (appstore/googleplay/trustpilot)
    backlink: str             # URL to original review
    brand: str                # Brand identifier
    app_identifier: str       # bundleId / packageName / businessUnitId
    rating: int               # Star rating (1-5)
    language: str             # ISO language code
    created_at: datetime      # When review was created
    fetched_at: datetime      # When review was collected
    
    # Optional fields
    title: Optional[str]      # Review title
    text: Optional[str]       # Review content
    country: Optional[str]    # ISO country code
    author_hint: Optional[str] # Username (no PII)
    is_processed: bool        # Processing flag
    content_hash: str         # SHA256 hash (auto-computed)
```

---

## 🎯 Reddit Post Structure

```json
{
  "id": "1nxu814",
  "title": "Asking for peace of mind.",
  "text": "Full post text...",
  "author": "okbirdywirdy",
  "subreddit": "birthcontrol",
  "score": 1,
  "upvote_ratio": 1.0,
  "num_comments": 8,
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

## 🔄 Mapping Strategy

### ✅ Direct Mappings (1:1)

| Reddit Field | Review Field | Transformation | Example |
|--------------|--------------|----------------|---------|
| `id` | `id` | Direct copy | `"1nxu814"` |
| `brand` | `brand` | Normalize (lowercase_with_underscores) | `"flo_app"` |
| `author` | `author_hint` | Direct copy | `"okbirdywirdy"` |
| `title` | `title` | Direct copy | `"Asking for peace of mind."` |
| `text` | `text` | Direct copy | `"Full post text..."` |
| `permalink` | `backlink` | Prepend base URL if needed | `"https://www.reddit.com/r/..."` |
| `created_date` | `created_at` | Parse to datetime | `datetime(2025, 10, 4, ...)` |

### 🔧 Computed/Derived Fields

| Review Field | Source | Logic | Example |
|--------------|--------|-------|---------|
| `source` | Constant | Always `"reddit"` | `ReviewSource.REDDIT` |
| `app_identifier` | `subreddit` | Use subreddit name | `"birthcontrol"` |
| `rating` | `score` + `upvote_ratio` | **See Rating Logic** | `4` |
| `language` | Detect from `text` | Use langdetect library | `"en"` |
| `country` | `None` or detect | Optional, can leave empty | `None` |
| `fetched_at` | Current time | `datetime.now(timezone.utc)` | `"2025-10-05..."` |
| `is_processed` | Constant | Always `False` initially | `False` |
| `content_hash` | Auto-computed | SHA256 of stable fields | `"abc123..."` |

### ⭐ Rating Logic (Critical Decision)

Reddit doesn't have star ratings (1-5), so we need to map score/upvote_ratio → rating.

**Option 1: Score-based (Simple)**
```python
def score_to_rating(score: int, upvote_ratio: float) -> int:
    """
    Map Reddit score to 1-5 rating scale.
    
    Score ranges:
    - <= 0: 1 star (negative)
    - 1-2: 2 stars (poor)
    - 3-10: 3 stars (neutral)
    - 11-50: 4 stars (good)
    - 50+: 5 stars (excellent)
    """
    if score <= 0:
        return 1
    elif score <= 2:
        return 2
    elif score <= 10:
        return 3
    elif score <= 50:
        return 4
    else:
        return 5
```

**Option 2: Upvote Ratio-based (More accurate)**
```python
def upvote_ratio_to_rating(upvote_ratio: float, score: int) -> int:
    """
    Map upvote ratio to 1-5 rating scale.
    
    Considers both ratio and absolute score:
    - <0.40: 1 star (controversial/negative)
    - 0.40-0.55: 2 stars
    - 0.55-0.70: 3 stars
    - 0.70-0.85: 4 stars
    - 0.85+: 5 stars
    
    If score is very low (0-1), cap at 3 stars max.
    """
    # Handle very low engagement
    if score <= 1:
        return min(3, int(upvote_ratio * 5) + 1)
    
    if upvote_ratio < 0.40:
        return 1
    elif upvote_ratio < 0.55:
        return 2
    elif upvote_ratio < 0.70:
        return 3
    elif upvote_ratio < 0.85:
        return 4
    else:
        return 5
```

**Option 3: Sentiment-based (Most sophisticated) ⭐ RECOMMENDED**
```python
def sentiment_to_rating(text: str, upvote_ratio: float) -> int:
    """
    Use sentiment analysis + upvote ratio.
    
    1. Analyze text sentiment (positive/neutral/negative)
    2. Adjust based on upvote_ratio
    3. Return 1-5 rating
    
    This gives most accurate representation of user opinion.
    """
    from textblob import TextBlob  # or use AWS Comprehend
    
    # Analyze sentiment
    blob = TextBlob(text or "")
    polarity = blob.sentiment.polarity  # -1 to 1
    
    # Convert to base rating (1-5)
    base_rating = int((polarity + 1) / 2 * 4) + 1  # Maps -1:1 to 1:5
    
    # Adjust with upvote_ratio
    if upvote_ratio < 0.5:
        base_rating = max(1, base_rating - 1)
    elif upvote_ratio > 0.9:
        base_rating = min(5, base_rating + 1)
    
    return max(1, min(5, base_rating))
```

**📝 Recommendation:** Use **Option 2** (Upvote Ratio-based) для початку, потім можна додати **Option 3** (Sentiment) для більшої точності.

---

## 🆕 Extended ReviewSource Enum

Потрібно додати Reddit до enum:

```python
# src/shared/domain/review.py

class ReviewSource(str, Enum):
    """Supported review sources"""
    APP_STORE = "appstore"
    GOOGLE_PLAY = "googleplay"
    TRUSTPILOT = "trustpilot"
    REDDIT = "reddit"  # ← NEW
```

---

## 📦 DynamoDB Schema

### Primary Key Format
```
pk = "reddit#{post_id}"
```
Example: `"reddit#1nxu814"`

### Full Item Example
```json
{
  "pk": "reddit#1nxu814",
  "id": "1nxu814",
  "source": "reddit",
  "backlink": "https://www.reddit.com/r/birthcontrol/comments/1nxu814/...",
  "brand": "flo_app",
  "app_identifier": "birthcontrol",
  "title": "Asking for peace of mind.",
  "text": "Hello everyone. I've read online...",
  "rating": 4,
  "language": "en",
  "country": "",
  "author_hint": "okbirdywirdy",
  "created_at": "2025-10-04T13:37:24+00:00",
  "fetched_at": "2025-10-05T02:20:05+00:00",
  "is_processed": false,
  "content_hash": "abc123...",
  
  // Reddit-specific extra fields (optional, for analytics)
  "reddit_score": 1,
  "reddit_upvote_ratio": 1.0,
  "reddit_num_comments": 8,
  "reddit_subreddit": "birthcontrol",
  "reddit_link_flair": "Mistake or Risk?",
  "reddit_over_18": false
}
```

### GSI Query Support
Existing GSI `brand-created_at-index` буде працювати:
```python
# Query all Reddit posts for brand
response = table.query(
    IndexName='brand-created_at-index',
    KeyConditionExpression='brand = :brand AND created_at > :date',
    ExpressionAttributeValues={
        ':brand': 'flo_app',
        ':date': '2025-10-01T00:00:00'
    }
)
```

---

## 🔨 Implementation Plan

### Step 1: Update Domain Model ✅
```python
# src/shared/domain/review.py

class ReviewSource(str, Enum):
    APP_STORE = "appstore"
    GOOGLE_PLAY = "googleplay"
    TRUSTPILOT = "trustpilot"
    REDDIT = "reddit"  # Add this
```

### Step 2: Create Reddit Client 🔄
```python
# src/reddit_collector/reddit_client.py

class RedditClient:
    """Client for Reddit API using PRAW"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(...)
    
    def search_brand_mentions(
        self, 
        brand: str,
        limit: int = 100,
        days_back: int = 30
    ) -> List[Dict]:
        """Search for brand mentions"""
        # Implementation from test_reddit.py
        pass
```

### Step 3: Create Reddit → Review Mapper 🔄
```python
# src/reddit_collector/reddit_mapper.py

from domain import Review, ReviewSource
from datetime import datetime, timezone
from typing import Dict

def map_reddit_post_to_review(
    post: Dict, 
    brand: str,
    fetched_at: datetime = None
) -> Review:
    """
    Map Reddit post to Review entity.
    
    Args:
        post: Reddit post data from PRAW
        brand: Brand identifier (normalized)
        fetched_at: Collection timestamp
    
    Returns:
        Review entity
    """
    if fetched_at is None:
        fetched_at = datetime.now(timezone.utc)
    
    # Parse created_at
    created_at = datetime.fromisoformat(post['created_date'])
    
    # Calculate rating from upvote ratio
    rating = upvote_ratio_to_rating(
        post['upvote_ratio'],
        post['score']
    )
    
    # Detect language
    language = detect_language(post['text'] or post['title'])
    
    return Review(
        id=post['id'],
        source=ReviewSource.REDDIT,
        backlink=post['permalink'],
        brand=brand,
        app_identifier=post['subreddit'],
        title=post['title'],
        text=post['text'],
        rating=rating,
        language=language,
        country=None,  # Reddit doesn't provide country
        author_hint=post['author'],
        created_at=created_at,
        fetched_at=fetched_at,
        is_processed=False
    )

def upvote_ratio_to_rating(upvote_ratio: float, score: int) -> int:
    """Convert upvote ratio to 1-5 star rating"""
    if score <= 1:
        return min(3, int(upvote_ratio * 5) + 1)
    
    if upvote_ratio < 0.40:
        return 1
    elif upvote_ratio < 0.55:
        return 2
    elif upvote_ratio < 0.70:
        return 3
    elif upvote_ratio < 0.85:
        return 4
    else:
        return 5

def detect_language(text: str) -> str:
    """Detect language from text"""
    try:
        from langdetect import detect
        return detect(text) if text else 'en'
    except:
        return 'en'  # Default to English
```

### Step 4: Create Lambda Handler 🔄
```python
# src/reddit_collector/handler.py

from reddit_client import RedditClient
from reddit_mapper import map_reddit_post_to_review
from infrastructure.repositories.dynamodb_review_repository import DynamoDBReviewRepository
from infrastructure.clients.secrets_client import SecretsClient
from utils.brand_normalizer import normalize_brand_for_storage

def lambda_handler(event, context):
    """
    Lambda handler for collecting Reddit posts.
    
    Event format:
    {
        "brand": "Flo app",
        "limit": 100,
        "days_back": 30,
        "job_id": "job_123" (optional)
    }
    """
    # Parse request
    brand = event['brand']
    limit = event.get('limit', 100)
    days_back = event.get('days_back', 30)
    job_id = event.get('job_id')
    
    # Normalize brand
    normalized_brand = normalize_brand_for_storage(brand)
    
    # Get credentials
    secrets = SecretsClient()
    creds = secrets.get_reddit_credentials()
    
    # Initialize client
    client = RedditClient(
        creds['client_id'],
        creds['client_secret'],
        creds['user_agent']
    )
    
    # Search posts
    posts = client.search_brand_mentions(brand, limit, days_back)
    
    # Map to reviews
    reviews = [
        map_reddit_post_to_review(post, normalized_brand)
        for post in posts
    ]
    
    # Save to DynamoDB
    repository = DynamoDBReviewRepository(job_id=job_id)
    stats = {
        'fetched': len(reviews),
        'saved': 0,
        'skipped': 0
    }
    
    for review in reviews:
        try:
            repository.save(review)
            stats['saved'] += 1
        except Exception as e:
            logger.warning(f"Failed to save {review.id}: {e}")
            stats['skipped'] += 1
    
    return {
        'success': True,
        'statistics': stats,
        'brand': normalized_brand
    }
```

### Step 5: Add to CDK Stack 🔄
```python
# cdk/stacks/review_collector_stack.py

# Add Reddit collector Lambda
reddit_lambda = self._create_reddit_collector_lambda(
    shared_layer=shared_layer,
    reviews_table=reviews_table
)

# Add to Step Functions workflow
reddit_task = tasks.LambdaInvoke(
    self, "CollectRedditPosts",
    lambda_function=reddit_lambda,
    payload=sfn.TaskInput.from_object({
        "brand": sfn.JsonPath.string_at("$.brand"),
        "limit": 100,
        "days_back": 30,
        "job_id": sfn.JsonPath.string_at("$.job_id")
    })
)
```

### Step 6: Add Secrets to AWS Secrets Manager 🔄
```bash
aws secretsmanager create-secret \
  --name reddit-api-credentials \
  --description "Reddit API credentials" \
  --secret-string '{
    "client_id": "Ao_QStxK9p0cS5875yH6Ag",
    "client_secret": "-Y65zQvx1EBPy9rIzUX0_TYRi5Z_Yw",
    "user_agent": "Brand Monitor v1.0"
  }'
```

---

## 🎯 Special Considerations

### 1. Reddit-Specific Metadata
Зберігаємо додаткові Reddit поля для аналітики:
- `reddit_score`: Upvotes - downvotes
- `reddit_upvote_ratio`: % upvotes
- `reddit_num_comments`: Comment count
- `reddit_subreddit`: Where posted
- `reddit_link_flair`: Post flair

### 2. Text Posts vs Link Posts
- **Text posts** (`is_self=true`): Має `text` поле
- **Link posts** (`is_self=false`): `text` порожнє, але є `url`

Рішення: Для link posts, додати URL до title/text для контексту.

### 3. Language Detection
Reddit не надає language field, потрібно детектувати:
```python
pip install langdetect
```

### 4. Rating Calibration
Після збору перших даних, можливо потрібно буде відкалібрувати формулу rating based on:
- Розподіл upvote_ratio
- Порівняння з sentiment analysis
- Feedback від бізнесу

---

## 📊 Expected Data Volume

За останній місяць для "Flo app":
- **Постів:** ~100
- **Subreddits:** 36 унікальних
- **Engagement:** 445 upvotes, 740 коментарів
- **Top subreddits:** r/amipregnant, r/Periods, r/birthcontrol

**Storage estimate:** ~50-100KB per post → 5-10MB per month

---

## ✅ Advantages of This Approach

1. **Unified Data Model** - Reddit posts разом з reviews в одній таблиці
2. **Existing Infrastructure** - Використовуємо існуючу ReviewRepository
3. **GSI Support** - Queries by brand/date працюють одразу
4. **Analytics Ready** - Додаткові Reddit поля для глибшого аналізу
5. **Extensible** - Легко додати інші соціальні мережі (Twitter, Instagram)

---

## 🚀 Next Steps

1. ✅ Оновити `ReviewSource` enum
2. 🔄 Створити `RedditClient` (базуємось на test_reddit.py)
3. 🔄 Створити `reddit_mapper.py` з маппінг логікою
4. 🔄 Створити Lambda handler
5. 🔄 Додати до CDK stack
6. 🔄 Додати credentials в Secrets Manager
7. 🔄 Протестувати end-to-end
8. 🔄 Додати в Step Functions workflow

---

**Готові почати імплементацію? 🎯**

