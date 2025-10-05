"""
Collect Reviews Use Case

Orchestrates the review collection process.
This is the application layer - coordinates domain and infrastructure.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from domain import ReviewRepository
from infrastructure.clients import BaseAPIClient


logger = logging.getLogger(__name__)


class CollectReviewsUseCase:
    """
    Use case for collecting reviews from a single source.
    
    Workflow:
    1. Authenticate API client
    2. Fetch reviews from API (with pagination)
    3. Save reviews to repository (idempotent)
    4. Return statistics
    """
    
    def __init__(
        self,
        api_client: BaseAPIClient,
        repository: ReviewRepository
    ):
        """
        Initialize use case.
        
        Args:
            api_client: API client for specific source
            repository: Repository for storing reviews
        """
        self.api_client = api_client
        self.repository = repository
        logger.info("Initialized CollectReviewsUseCase")
    
    def execute(
        self,
        credentials: Dict[str, str],
        app_identifier: str,
        brand: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute review collection workflow.
        
        Args:
            credentials: API credentials from Secrets Manager
            app_identifier: App/business identifier
            brand: Brand name
            since: Fetch reviews created after this timestamp
            limit: Maximum number of reviews to fetch
            
        Returns:
            Statistics dict with counts and timing
        """
        start_time = datetime.utcnow()
        stats = {
            'brand': brand,
            'app_identifier': app_identifier,
            'fetched': 0,
            'saved': 0,
            'skipped': 0,
            'errors': 0,
            'start_time': start_time.isoformat(),
        }
        
        try:
            # Step 1: Authenticate
            logger.info(f"Authenticating API client for {app_identifier}")
            self.api_client.authenticate(credentials)
            
            # Step 2: Fetch reviews
            logger.info(f"Fetching reviews for {app_identifier} (since: {since}, limit: {limit})")
            reviews = self.api_client.fetch_reviews(
                app_identifier=app_identifier,
                since=since,
                limit=limit,
                brand=brand
            )
            stats['fetched'] = len(reviews)
            logger.info(f"Fetched {len(reviews)} reviews")
            
            # Step 3: Save reviews (idempotent)
            logger.info(f"Saving reviews to repository")
            for review in reviews:
                try:
                    saved = self.repository.save(review)
                    if saved:
                        stats['saved'] += 1
                    else:
                        stats['skipped'] += 1
                except Exception as e:
                    logger.error(f"Failed to save review {review.id}: {e}")
                    stats['errors'] += 1
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            stats['duration_seconds'] = duration
            stats['end_time'] = end_time.isoformat()
            
            logger.info(f"Collection complete: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"Use case execution failed: {e}", exc_info=True)
            stats['error'] = str(e)
            stats['end_time'] = datetime.utcnow().isoformat()
            raise
        
        finally:
            # Cleanup
            self.api_client.close()

