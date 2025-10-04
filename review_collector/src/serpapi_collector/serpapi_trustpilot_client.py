"""
SerpAPI Trustpilot Client

Fetches reviews from Trustpilot using SerpAPI.
SerpAPI Docs: https://serpapi.com/trustpilot
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from serpapi_base_client import SerpAPIBaseClient

# Import from Lambda Layer (located in /opt/python/)
from domain.review import Review, ReviewSource


logger = logging.getLogger(__name__)


class SerpAPITrustpilotClient(SerpAPIBaseClient):
    """
    Trustpilot review collector using SerpAPI.
    
    Works with any public Trustpilot business page - no Trustpilot API key needed!
    
    Example identifiers:
    - Tesla: "tesla.com"
    - Amazon: "amazon.com"
    - Booking.com: "booking.com"
    """
    
    def fetch_reviews(
        self,
        app_identifier: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
        brand: str = ''
    ) -> List[Review]:
        """
        Fetch reviews from Trustpilot via SerpAPI.
        
        Args:
            app_identifier: Domain name (e.g. "tesla.com")
            since: Not supported by SerpAPI (ignored)
            limit: Maximum number of reviews (default: 100, max: 20 per request)
            
        Returns:
            List of normalized Review entities
        """
        logger.info(f"Fetching Trustpilot reviews for domain={app_identifier}")
        
        if since:
            logger.warning("'since' parameter not supported by SerpAPI - ignored")
        
        limit = limit or 100
        reviews = []
        
        # SerpAPI returns max 20 reviews per request for Trustpilot
        # For more, would need pagination
        num_per_request = min(limit, 20)
        
        params = {
            'engine': 'trustpilot',
            'domain': app_identifier,
            'num': num_per_request,
        }
        
        try:
            results = self._execute_search(params)
            
            # Extract reviews from response
            reviews_data = results.get('reviews', [])
            logger.info(f"Received {len(reviews_data)} reviews from SerpAPI")
            
            # Parse each review
            for item in reviews_data:
                try:
                    review = self._normalize_review(item, brand, app_identifier)
                    reviews.append(review)
                except Exception as e:
                    logger.error(f"Failed to normalize review: {e}")
                    logger.debug(f"Raw review data: {item}")
                    continue
            
            logger.info(f"Successfully parsed {len(reviews)} Trustpilot reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Failed to fetch Trustpilot reviews: {e}")
            raise
    
    def _normalize_review(
        self,
        raw_data: Dict[str, Any],
        brand: str,
        app_identifier: str
    ) -> Review:
        """
        Normalize SerpAPI Trustpilot review to Review entity.
        
        SerpAPI response structure:
        {
            "rating": 5,
            "title": "Excellent service",
            "text": "I had a great experience...",
            "author": {
                "name": "John D.",
                "reviews": 5
            },
            "date": "2024-10-01",
            "location": "US"
        }
        """
        # Extract fields with safe defaults
        rating = int(raw_data.get('rating', 0))
        title = raw_data.get('title', '')
        text = raw_data.get('text', '')
        date_str = raw_data.get('date', '')
        
        # Extract author info
        author_data = raw_data.get('author', {})
        if isinstance(author_data, dict):
            author = author_data.get('name', '')
        else:
            author = str(author_data) if author_data else ''
        
        # Extract location
        location = raw_data.get('location', '')
        
        # Generate unique ID (SerpAPI doesn't provide review IDs)
        import hashlib
        id_content = f"{app_identifier}_{author}_{title}_{date_str}"
        review_id = hashlib.md5(id_content.encode()).hexdigest()
        
        # Parse date
        try:
            # SerpAPI date format: "2024-10-01" or "October 1, 2024"
            if '-' in date_str:
                created_at = datetime.fromisoformat(date_str)
            else:
                # Try parsing "October 1, 2024" format
                created_at = datetime.strptime(date_str, "%B %d, %Y")
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse date: {date_str}")
            created_at = datetime.utcnow()
        
        # Generate backlink
        backlink = f"https://www.trustpilot.com/review/{app_identifier}"
        
        return Review(
            id=review_id,
            source=ReviewSource.TRUSTPILOT,
            backlink=backlink,
            brand=brand,
            app_identifier=app_identifier,
            title=title or None,
            text=text or None,
            rating=rating,
            language='en',  # SerpAPI doesn't always provide language
            country=location if location else None,
            author_hint=author or None,
            created_at=created_at,
            fetched_at=datetime.utcnow()
        )

