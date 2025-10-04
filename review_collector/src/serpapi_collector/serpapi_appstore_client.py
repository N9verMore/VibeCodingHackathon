"""
SerpAPI App Store Client

Fetches reviews from Apple App Store using SerpAPI.
SerpAPI Docs: https://serpapi.com/apple-app-store
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from serpapi_base_client import SerpAPIBaseClient

# Import from Lambda Layer (located in /opt/python/)
from domain.review import Review, ReviewSource


logger = logging.getLogger(__name__)


class SerpAPIAppStoreClient(SerpAPIBaseClient):
    """
    App Store review collector using SerpAPI.
    
    Works with any public App Store app - no Apple Developer account needed!
    
    Example identifiers:
    - Telegram: "544007664"
    - WhatsApp: "310633997"
    - Instagram: "389801252"
    """
    
    def fetch_reviews(
        self,
        app_identifier: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
        brand: str = ''
    ) -> List[Review]:
        """
        Fetch reviews from App Store via SerpAPI.
        
        Args:
            app_identifier: Apple App ID (numeric, e.g. "544007664")
            since: Not supported by SerpAPI (ignored)
            limit: Maximum number of reviews (default: 100, max: 50 per request)
            
        Returns:
            List of normalized Review entities
        """
        logger.info(f"Fetching App Store reviews for app_id={app_identifier}")
        
        if since:
            logger.warning("'since' parameter not supported by SerpAPI - ignored")
        
        limit = limit or 100
        reviews = []
        
        # SerpAPI pagination - collect multiple pages
        # According to https://serpapi.com/apple-reviews uses 'page' parameter
        page_num = 1
        max_pages = (limit + 24) // 25  # ~25 reviews per page for App Store
        
        try:
            while len(reviews) < limit and page_num <= max_pages:
                params = {
                    'engine': 'apple_reviews',
                    'product_id': app_identifier,
                    'country': 'us',
                    'page': str(page_num),  # Page number for pagination
                    'sort': 'mostrecent',   # Sort by most recent
                }
                
                logger.info(f"Fetching page {page_num} (collected {len(reviews)} so far)")
                results = self._execute_search(params)
                
                # Extract reviews from response
                reviews_data = results.get('reviews', [])
                logger.info(f"Received {len(reviews_data)} reviews on page {page_num}")
                
                if not reviews_data:
                    logger.info("No more reviews available")
                    break
                
                # Parse each review
                for idx, item in enumerate(reviews_data):
                    if len(reviews) >= limit:
                        break
                    try:
                        if idx == 0 and page_num == 1:  # Log first review for debugging
                            logger.info(f"Sample review structure: {item}")
                        review = self._normalize_review(item, brand, app_identifier)
                        reviews.append(review)
                    except Exception as e:
                        logger.error(f"Failed to normalize review: {e}")
                        logger.error(f"Raw review data: {item}")
                        continue
                
                # Check for next page in pagination info
                serpapi_pagination = results.get('serpapi_pagination', {})
                has_next = 'next' in serpapi_pagination
                
                if not has_next:
                    logger.info("No more pages available")
                    break
                
                page_num += 1
            
            logger.info(f"Successfully parsed {len(reviews)} App Store reviews across {page_num} pages")
            return reviews
            
        except Exception as e:
            logger.error(f"Failed to fetch App Store reviews: {e}")
            raise
    
    def _normalize_review(
        self,
        raw_data: Dict[str, Any],
        brand: str,
        app_identifier: str
    ) -> Review:
        """
        Normalize SerpAPI App Store review to Review entity.
        
        SerpAPI response structure:
        {
            "rating": 5,
            "title": "Great app!",
            "review": "This is the best messaging app...",
            "author": "John D.",
            "date": "2024-10-01",
            "version": "10.0.1"
        }
        """
        # Extract fields with safe defaults
        rating = int(raw_data.get('rating', 0))
        title = raw_data.get('title', '')
        text = raw_data.get('text', '')  # SerpAPI uses 'text' not 'review'
        
        # Author is a dict with 'name' and 'author_id'
        author_data = raw_data.get('author', {})
        author = author_data.get('name', '') if isinstance(author_data, dict) else str(author_data)
        
        date_str = raw_data.get('review_date', '')  # SerpAPI uses 'review_date' not 'date'
        version = raw_data.get('reviewed_version', '').replace('Version ', '')  # Remove 'Version ' prefix
        
        # Generate unique ID (SerpAPI doesn't provide review IDs)
        # Use hash of content as ID
        import hashlib
        id_content = f"{app_identifier}_{author}_{title}_{date_str}"
        review_id = hashlib.md5(id_content.encode()).hexdigest()
        
        # Parse date
        try:
            # SerpAPI date format: "2024-10-01" or "Oct 1, 2024"
            if '-' in date_str:
                created_at = datetime.fromisoformat(date_str)
            else:
                # Try parsing "Oct 1, 2024" format
                created_at = datetime.strptime(date_str, "%b %d, %Y")
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse date: {date_str}")
            created_at = datetime.utcnow()
        
        # Generate backlink
        backlink = f"https://apps.apple.com/app/id{app_identifier}?see-all=reviews"
        
        return Review(
            id=review_id,
            source=ReviewSource.APP_STORE,
            backlink=backlink,
            brand=brand,
            app_identifier=app_identifier,
            title=title or None,
            text=text or None,
            rating=rating,
            language='en',  # SerpAPI doesn't always provide language
            country=None,    # SerpAPI doesn't provide country in basic response
            author_hint=author or None,
            created_at=created_at,
            fetched_at=datetime.utcnow()
        )

