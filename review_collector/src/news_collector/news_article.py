"""
NewsArticle Entity - Domain Model

Represents a news article from NewsAPI.
Independent from Review entity - designed specifically for news data.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class NewsArticle:
    """
    News article entity with validation and content hashing.
    
    Attributes:
        id: Unique article ID (generated from source + publishedAt)
        source_id: News source identifier (e.g., 'bbc-news', 'cnn')
        source_name: Human-readable source name (e.g., 'BBC News')
        url: URL to original article
        brand: Search term/keyword used (e.g., 'tesla', 'apple')
        title: Article headline
        description: Brief description/summary
        content: Full article content (truncated by NewsAPI)
        author: Article author(s)
        published_at: When article was published
        fetched_at: When article was collected
        image_url: URL to article image (optional)
        language: ISO language code (e.g., 'en', 'uk')
        country: ISO country code (optional, e.g., 'us', 'ua')
        is_processed: Flag indicating if article has been processed
        content_hash: SHA256 hash of stable fields (auto-computed)
    """
    
    id: str
    source_id: str
    source_name: str
    url: str
    brand: str
    title: str
    published_at: datetime
    fetched_at: datetime
    description: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    language: str = "en"
    country: Optional[str] = None
    is_processed: bool = False
    content_hash: str = field(init=False)
    
    def __post_init__(self):
        """Validate fields and compute content hash"""
        self._validate()
        self.content_hash = self._compute_hash()
    
    def _validate(self):
        """Validate article data"""
        if not self.id:
            raise ValueError("Article ID cannot be empty")
        
        if not self.source_id:
            raise ValueError("Source ID cannot be empty")
        
        if not self.url:
            raise ValueError("URL cannot be empty")
        
        if not self.brand:
            raise ValueError("Brand/search term cannot be empty")
        
        if not self.title:
            raise ValueError("Title cannot be empty")
        
        if len(self.language) < 2:
            raise ValueError(f"Invalid language code: {self.language}")
    
    def _compute_hash(self) -> str:
        """
        Compute SHA256 hash of stable fields (excluding fetched_at).
        Used for idempotency - same content = same hash.
        """
        stable_fields = [
            self.id,
            self.source_id,
            self.source_name,
            self.url,
            self.brand,
            self.title,
            self.description or "",
            self.content or "",
            self.author or "",
            self.language,
            self.country or "",
            self.published_at.isoformat(),
        ]
        
        content = "|".join(stable_fields)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def to_dynamodb_item(self) -> dict:
        """
        Convert to DynamoDB item format.
        Uses same table as reviews but with 'news' source prefix.
        """
        return {
            'pk': f"news#{self.id}",  # Composite primary key
            'id': self.id,
            'source': 'news',  # Constant for all news articles
            'source_id': self.source_id,
            'source_name': self.source_name,
            'backlink': self.url,  # Reuse 'backlink' field from Review schema
            'brand': self.brand,
            'app_identifier': self.source_id,  # Reuse existing field for source_id
            'title': self.title or '',
            'text': self._combine_text(),  # Combine description + content
            'rating': -1,  # Use -1 to indicate "not applicable" for news
            'description': self.description or '',
            'content': self.content or '',
            'author_hint': self.author or '',  # Reuse author_hint field
            'image_url': self.image_url or '',
            'language': self.language,
            'country': self.country or '',
            'created_at': self.published_at.isoformat(),  # Map published_at to created_at
            'fetched_at': self.fetched_at.isoformat(),
            'is_processed': self.is_processed,
            'content_hash': self.content_hash,
        }
    
    def _combine_text(self) -> str:
        """Combine description and content into single text field"""
        parts = []
        if self.description:
            parts.append(self.description)
        if self.content:
            parts.append(self.content)
        return "\n\n".join(parts)
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'NewsArticle':
        """Create NewsArticle from DynamoDB item"""
        return cls(
            id=item['id'],
            source_id=item['source_id'],
            source_name=item['source_name'],
            url=item['backlink'],
            brand=item['brand'],
            title=item.get('title') or '',
            description=item.get('description'),
            content=item.get('content'),
            author=item.get('author_hint'),
            image_url=item.get('image_url'),
            language=item['language'],
            country=item.get('country'),
            published_at=datetime.fromisoformat(item['created_at']),
            fetched_at=datetime.fromisoformat(item['fetched_at']),
            is_processed=item.get('is_processed', False),
        )

