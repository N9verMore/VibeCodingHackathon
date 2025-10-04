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
    Uses Apple App Store API: https://serpapi.com/apple-app-store
    Uses Apple Reviews API: https://serpapi.com/apple-reviews-api
    
    Example identifiers:
    - Telegram: "544007664"
    - WhatsApp: "310633997"
    - Instagram: "389801252"
    """
    
    def get_app_info(self, app_identifier: str, country: str = 'us') -> Dict[str, Any]:
        """
        Fetch app metadata from App Store.
        
        Args:
            app_identifier: Apple App ID (numeric, e.g. "544007664")
            country: Country code (e.g. 'us', 'gb')
            
        Returns:
            Dict with app info (title, rating, developer, etc.)
        """
        params = {
            'engine': 'apple_product',
            'product_id': app_identifier,
            'country': country,
            'type': 'app',
        }
        
        results = self._execute_search(params)
        
        # Extract rating info
        rating_info = results.get('rating', [])
        rating_value = None
        rating_count = None
        if rating_info:
            # Get 'All Times' rating if available
            for r in rating_info:
                if r.get('type') == 'All Times':
                    rating_value = r.get('rating')
                    rating_count = r.get('count')
                    break
        
        # Extract developer info
        developer_info = results.get('developer', {})
        developer_name = developer_info.get('name') if isinstance(developer_info, dict) else None
        
        # Extract price info
        price_info = results.get('price', {})
        price_type = price_info.get('type') if isinstance(price_info, dict) else None
        
        return {
            'title': results.get('title'),
            'bundle_id': results.get('bundle_id'),
            'rating': rating_value,
            'rating_count': rating_count,
            'description': results.get('description'),
            'developer': developer_name,
            'developer_id': developer_info.get('id') if isinstance(developer_info, dict) else None,
            'version': results.get('version'),
            'release_date': results.get('release_date'),
            'latest_version_release_date': results.get('latest_version_release_date'),
            'price_type': price_type,
            'age_rating': results.get('age_rating'),
            'size_in_bytes': results.get('size_in_bytes'),
            'link': results.get('link'),
            'genres': results.get('genres', []),
        }
    
    def fetch_reviews(
        self,
        app_identifier: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
        brand: str = ''
    ) -> List[Review]:
        """
        Fetch reviews from App Store via SerpAPI.
        
        Reviews are sorted by most recent (sort='mostrecent').
        
        Args:
            app_identifier: Apple App ID (numeric, e.g. "544007664")
            since: Not supported by SerpAPI (ignored)
            limit: Maximum number of reviews (default: 100, max: 50 per request)
            
        Returns:
            List of normalized Review entities sorted by most recent first
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
                
                logger.info(f"Fetching App Store page {page_num} (collected {len(reviews)}/{limit} reviews)")
                results = self._execute_search(params)
                
                # Log app info on first page
                if page_num == 1:
                    app_title = results.get('product_name', 'Unknown')
                    app_rating = results.get('product_rating', 'N/A')
                    app_reviews_count = results.get('product_num_reviews', 'N/A')
                    logger.info(f"App: {app_title} | Rating: {app_rating} | Total Reviews: {app_reviews_count}")
                
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
                        if idx == 0 and page_num == 1:  # Log first review structure for debugging
                            logger.debug(f"Sample review structure: {list(item.keys())}")
                        review = self._normalize_review(item, brand, app_identifier)
                        reviews.append(review)
                    except Exception as e:
                        logger.error(f"Failed to normalize review: {e}")
                        logger.debug(f"Raw review data: {item}")
                        continue
                
                # Check for next page in pagination info
                # Reference: https://serpapi.com/apple-reviews-api (serpapi_pagination section)
                serpapi_pagination = results.get('serpapi_pagination', {})
                has_next = 'next' in serpapi_pagination
                
                if not has_next:
                    logger.info("No more pages available (no 'next' in pagination)")
                    break
                
                page_num += 1
            
            logger.info(f"✓ Successfully collected {len(reviews)} App Store reviews across {page_num} page(s)")
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
        
        SerpAPI Apple Reviews API response structure:
        Reference: https://serpapi.com/apple-reviews-api
        
        {
            "position": 1,
            "rating": 5,
            "title": "Great app!",
            "text": "This is the best messaging app...",
            "author": {
                "name": "John D.",
                "link": "https://..."
            },
            "review_date": "October 1, 2024",
            "reviewed_version": "Version 10.0.1",
            "review_id": "12345678"
        }
        """
        # Extract fields with safe defaults
        rating = int(raw_data.get('rating', 0))
        title = raw_data.get('title', '')
        text = raw_data.get('text', '')  # Review body text
        
        # Author is a dict with 'name' and potentially 'link'
        author_data = raw_data.get('author', {})
        author_name = None
        if isinstance(author_data, dict):
            author_name = author_data.get('name', '')
        elif author_data:
            author_name = str(author_data)
        
        date_str = raw_data.get('review_date', '')
        version = raw_data.get('reviewed_version', '')
        if version and version.startswith('Version '):
            version = version.replace('Version ', '')  # Remove 'Version ' prefix
        
        # Use review_id if available, otherwise generate hash
        review_id = raw_data.get('review_id')
        if not review_id:
            import hashlib
            id_content = f"{app_identifier}_{author_name}_{title}_{text[:50]}_{date_str}_{rating}"
            review_id = hashlib.md5(id_content.encode()).hexdigest()
        else:
            review_id = str(review_id)
        
        # Parse date
        try:
            # SerpAPI date format: "October 1, 2024" or "2024-10-01"
            if date_str:
                if '-' in date_str:
                    created_at = datetime.fromisoformat(date_str)
                else:
                    # Try parsing "October 1, 2024" format
                    created_at = datetime.strptime(date_str, "%B %d, %Y")
            else:
                created_at = datetime.utcnow()
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            created_at = datetime.utcnow()
        
        # Generate backlink to reviews section
        backlink = f"https://apps.apple.com/app/id{app_identifier}?see-all=reviews"
        
        # Combine title and text for full review content
        full_text = f"{title}\n\n{text}" if title and text else (title or text)
        
        return Review(
            id=review_id,
            source=ReviewSource.APP_STORE,
            backlink=backlink,
            brand=brand,
            app_identifier=app_identifier,
            title=title or None,
            text=full_text or None,
            rating=rating,
            language='en',  # SerpAPI doesn't always provide language
            country='us',    # We're requesting 'us' in params
            author_hint=author_name or None,
            created_at=created_at,
            fetched_at=datetime.utcnow()
        )

