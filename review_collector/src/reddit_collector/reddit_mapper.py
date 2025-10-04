"""
Reddit Post to Review Mapper

Maps Reddit posts to the standardized Review entity.
"""

import logging
from typing import Dict
from datetime import datetime, timezone

# Will be imported from Lambda Layer
import sys
sys.path.insert(0, '/opt/python')

from domain import Review, ReviewSource


logger = logging.getLogger(__name__)


def map_reddit_post_to_review(
    post: Dict, 
    brand: str,
    fetched_at: datetime = None
) -> Review:
    """
    Map Reddit post to Review entity.
    
    Args:
        post: Reddit post data from RedditClient
        brand: Brand identifier (normalized)
        fetched_at: Collection timestamp (defaults to now)
    
    Returns:
        Review entity with rating=-1 (Reddit posts don't have ratings)
    """
    if fetched_at is None:
        fetched_at = datetime.now(timezone.utc)
    
    # Parse created_at
    created_at = datetime.fromisoformat(post['created_date'])
    
    # Detect language from text
    language = detect_language(post['text'] or post['title'])
    
    # Combine title and text for full content
    # For link posts, include URL
    text_content = post['text']
    if not text_content and not post['is_self']:
        text_content = f"[Link post: {post['url']}]"
    
    return Review(
        id=post['id'],
        source=ReviewSource.REDDIT,
        backlink=post['permalink'],
        brand=brand,
        app_identifier=post['subreddit'],  # Use subreddit as identifier
        title=post['title'],
        text=text_content,
        rating=-1,  # Reddit posts don't have star ratings
        language=language,
        country=None,  # Reddit doesn't provide country info
        author_hint=post['author'],
        created_at=created_at,
        fetched_at=fetched_at,
        is_processed=False
    )


def detect_language(text: str) -> str:
    """
    Detect language from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        ISO language code (defaults to 'en' if detection fails)
    """
    if not text or len(text.strip()) < 10:
        return 'en'  # Default to English for short/empty text
    
    try:
        from langdetect import detect
        detected = detect(text)
        logger.debug(f"Detected language: {detected}")
        return detected
    except Exception as e:
        logger.warning(f"Language detection failed: {e}, defaulting to 'en'")
        return 'en'

