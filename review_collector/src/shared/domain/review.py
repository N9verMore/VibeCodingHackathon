"""
Review Entity - Domain Model

Pure domain object with no external dependencies.
Represents a normalized review from any source.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class ReviewSource(str, Enum):
    """Supported review sources"""
    APP_STORE = "appstore"
    GOOGLE_PLAY = "googleplay"
    TRUSTPILOT = "trustpilot"
    REDDIT = "reddit"


@dataclass
class Review:
    """
    Normalized review entity with validation and content hashing.
    
    Attributes:
        id: Unique review ID from source platform
        source: Platform where review originated
        backlink: URL to original review
        brand: Brand/company identifier
        app_identifier: bundleId / packageName / businessUnitId
        title: Review title (optional)
        text: Review content (optional)
        rating: Star rating (1-5, or -1 for sources without ratings like Reddit)
        language: ISO language code (e.g., 'en', 'uk')
        country: ISO country code (optional, e.g., 'US', 'UA')
        author_hint: Username/nickname without PII
        created_at: When review was created
        fetched_at: When review was collected
        is_processed: Flag indicating if review has been processed
        content_hash: SHA256 hash of stable fields (auto-computed)
    """
    
    id: str
    source: ReviewSource
    backlink: str
    brand: str
    app_identifier: str
    rating: int
    language: str
    created_at: datetime
    fetched_at: datetime
    title: Optional[str] = None
    text: Optional[str] = None
    country: Optional[str] = None
    author_hint: Optional[str] = None
    is_processed: bool = False
    content_hash: str = field(init=False)
    
    def __post_init__(self):
        """Validate fields and compute content hash"""
        self._validate()
        self.content_hash = self._compute_hash()
    
    def _validate(self):
        """Validate review data"""
        if not self.id:
            raise ValueError("Review ID cannot be empty")
        
        if not isinstance(self.source, ReviewSource):
            raise ValueError(f"Invalid source: {self.source}")
        
        if not (self.rating == -1 or 1 <= self.rating <= 5):
            raise ValueError(f"Rating must be -1 (no rating) or 1-5, got {self.rating}")
        
        if not self.brand:
            raise ValueError("Brand cannot be empty")
        
        if not self.app_identifier:
            raise ValueError("App identifier cannot be empty")
        
        if len(self.language) < 2:
            raise ValueError(f"Invalid language code: {self.language}")
    
    def _compute_hash(self) -> str:
        """
        Compute SHA256 hash of stable fields (excluding fetched_at).
        Used for idempotency - same content = same hash.
        """
        stable_fields = [
            self.id,
            self.source.value,
            self.brand,
            self.app_identifier,
            self.title or "",
            self.text or "",
            str(self.rating),
            self.language,
            self.country or "",
            self.author_hint or "",
            self.created_at.isoformat(),
        ]
        
        content = "|".join(stable_fields)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format"""
        return {
            'pk': f"{self.source.value}#{self.id}",  # Composite primary key
            'id': self.id,
            'source': self.source.value,
            'backlink': self.backlink,
            'brand': self.brand,
            'app_identifier': self.app_identifier,
            'title': self.title or '',
            'text': self.text or '',
            'rating': self.rating,
            'language': self.language,
            'country': self.country or '',
            'author_hint': self.author_hint or '',
            'created_at': self.created_at.isoformat(),
            'fetched_at': self.fetched_at.isoformat(),
            'is_processed': self.is_processed,
            'content_hash': self.content_hash,
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Review':
        """Create Review from DynamoDB item"""
        return cls(
            id=item['id'],
            source=ReviewSource(item['source']),
            backlink=item['backlink'],
            brand=item['brand'],
            app_identifier=item['app_identifier'],
            title=item.get('title') or None,
            text=item.get('text') or None,
            rating=int(item['rating']),
            language=item['language'],
            country=item.get('country') or None,
            author_hint=item.get('author_hint') or None,
            created_at=datetime.fromisoformat(item['created_at']),
            fetched_at=datetime.fromisoformat(item['fetched_at']),
            is_processed=item.get('is_processed', False),
        )

