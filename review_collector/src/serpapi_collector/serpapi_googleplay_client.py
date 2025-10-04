"""
SerpAPI Google Play Client

Fetches reviews from Google Play Store using SerpAPI.
SerpAPI Docs: https://serpapi.com/google-play-product
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from serpapi_base_client import SerpAPIBaseClient

# Import from Lambda Layer (located in /opt/python/)
from domain.review import Review, ReviewSource


logger = logging.getLogger(__name__)


class SerpAPIGooglePlayClient(SerpAPIBaseClient):
    """
    Google Play review collector using SerpAPI.
    
    Works with any public Google Play app - no Google Play Console access needed!
    
    Example identifiers:
    - Telegram: "org.telegram.messenger"
    - WhatsApp: "com.whatsapp"
    - Instagram: "com.instagram.android"
    """
    
    def fetch_reviews(
        self,
        app_identifier: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
        brand: str = ''
    ) -> List[Review]:
        """
        Fetch reviews from Google Play via SerpAPI.
        
        Args:
            app_identifier: Package name (e.g. "org.telegram.messenger")
            since: Not supported by SerpAPI (ignored)
            limit: Maximum number of reviews (default: 100, max: 199)
            
        Returns:
            List of normalized Review entities
        """
        logger.info(f"Fetching Google Play reviews for package={app_identifier}")
        
        if since:
            logger.warning("'since' parameter not supported by SerpAPI - ignored")
        
        limit = limit or 100
        reviews = []
        
        # SerpAPI pagination - collect multiple pages
        page_num = 1
        max_pages = (limit + 19) // 20  # Calculate how many pages needed (20 reviews per page)
        next_page_token = None
        
        try:
            while len(reviews) < limit and page_num <= max_pages:
                params = {
                    'engine': 'google_play_product',
                    'product_id': app_identifier,
                    'store': 'apps',
                }
                
                # Add next_page_token for pagination (page 2+)
                if next_page_token:
                    params['next_page_token'] = next_page_token
                
                logger.info(f"Fetching page {page_num} (collected {len(reviews)} so far)")
                results = self._execute_search(params)
                
                # Extract reviews from response
                reviews_data = results.get('reviews', [])
                logger.info(f"Received {len(reviews_data)} reviews on page {page_num}")
                
                if not reviews_data:
                    logger.info("No more reviews available")
                    break
                
                # Parse each review
                for item in reviews_data:
                    if len(reviews) >= limit:
                        break
                    try:
                        review = self._normalize_review(item, brand, app_identifier)
                        reviews.append(review)
                    except Exception as e:
                        logger.error(f"Failed to normalize review: {e}")
                        logger.debug(f"Raw review data: {item}")
                        continue
                
                # Check for next page
                serpapi_pagination = results.get('serpapi_pagination', {})
                next_page_token = serpapi_pagination.get('next_page_token')
                
                if not next_page_token:
                    logger.info("No more pages available")
                    break
                
                page_num += 1
            
            logger.info(f"Successfully parsed {len(reviews)} Google Play reviews across {page_num} pages")
            return reviews
            
        except Exception as e:
            logger.error(f"Failed to fetch Google Play reviews: {e}")
            raise
    
    def _normalize_review(
        self,
        raw_data: Dict[str, Any],
        brand: str,
        app_identifier: str
    ) -> Review:
        """
        Normalize SerpAPI Google Play review to Review entity.
        
        SerpAPI response structure:
        {
            "rating": 5,
            "title": "Great app!",
            "snippet": "This is the best messaging app...",
            "likes": 42,
            "date": "October 1, 2024",
            "response": "Thank you for your feedback!",  # developer response
            "version": "10.0.1"
        }
        """
        # Extract fields with safe defaults
        rating = int(raw_data.get('rating', 0))
        title = raw_data.get('title', '')
        text = raw_data.get('snippet', '')
        date_str = raw_data.get('date', '')
        version = raw_data.get('version', '')
        likes = raw_data.get('likes', 0)
        
        # Generate unique ID (SerpAPI doesn't provide review IDs)
        import hashlib
        id_content = f"{app_identifier}_{title}_{text[:50]}_{date_str}"
        review_id = hashlib.md5(id_content.encode()).hexdigest()
        
        # Parse date
        try:
            # SerpAPI date format: "October 1, 2024" or "2024-10-01"
            if '-' in date_str:
                created_at = datetime.fromisoformat(date_str)
            else:
                # Try parsing "October 1, 2024" format
                created_at = datetime.strptime(date_str, "%B %d, %Y")
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse date: {date_str}")
            created_at = datetime.utcnow()
        
        # Generate backlink
        backlink = f"https://play.google.com/store/apps/details?id={app_identifier}&showAllReviews=true"
        
        return Review(
            id=review_id,
            source=ReviewSource.GOOGLE_PLAY,
            backlink=backlink,
            brand=brand,
            app_identifier=app_identifier,
            title=title or None,
            text=text or None,
            rating=rating,
            language='en',  # SerpAPI doesn't always provide language
            country=None,    # SerpAPI doesn't provide country in basic response
            author_hint=None,  # SerpAPI Google Play doesn't include author names
            created_at=created_at,
            fetched_at=datetime.utcnow()
        )

