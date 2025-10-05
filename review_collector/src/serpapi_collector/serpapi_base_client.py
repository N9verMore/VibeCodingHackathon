"""
SerpAPI Base Client

Base class for all SerpAPI-based review collectors.
Provides common functionality for authentication and request handling.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from serpapi import GoogleSearch

# Import from Lambda Layer (located in /opt/python/)
from infrastructure.clients.base_api_client import BaseAPIClient
from domain.review import Review


logger = logging.getLogger(__name__)


class SerpAPIBaseClient(BaseAPIClient):
    """
    Base class for SerpAPI clients.
    
    Provides common functionality:
    - API key management
    - Rate limiting handling
    - Error handling and retries
    - Request logging
    """
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize SerpAPI client.
        
        Args:
            api_key: SerpAPI API key
            timeout: Request timeout in seconds
        """
        super().__init__(timeout)
        self.api_key = api_key
        
        if not self.api_key:
            raise ValueError("SerpAPI key is required")
        
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def authenticate(self, credentials: Dict[str, str]) -> None:
        """
        No-op for SerpAPI (key passed in constructor).
        Kept for interface compatibility.
        """
        pass
    
    def fetch_reviews(
        self,
        app_identifier: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Review]:
        """
        Abstract method - must be implemented by subclasses.
        
        Args:
            app_identifier: App/product identifier
            since: Fetch reviews created after this timestamp (may not be supported)
            limit: Maximum number of reviews
            
        Returns:
            List of normalized Review entities
        """
        raise NotImplementedError("Subclass must implement fetch_reviews()")
    
    def _execute_search(
        self,
        params: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute SerpAPI search with retry logic.
        
        Args:
            params: Search parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            SerpAPI response dictionary
        """
        params['api_key'] = self.api_key
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Executing SerpAPI search (attempt {attempt + 1}/{max_retries})")
                logger.debug(f"Parameters: {self._sanitize_params(params)}")
                
                search = GoogleSearch(params)
                results = search.get_dict()
                
                # Check for errors in response
                if 'error' in results:
                    error_msg = results['error']
                    logger.error(f"SerpAPI error: {error_msg}")
                    
                    # Rate limit - wait and retry
                    if 'rate limit' in error_msg.lower():
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    
                    raise RuntimeError(f"SerpAPI error: {error_msg}")
                
                logger.info("SerpAPI search completed successfully")
                return results
                
            except Exception as e:
                logger.error(f"Search attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    raise
                
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        raise RuntimeError("Max retries exceeded")
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from params for logging"""
        sanitized = params.copy()
        if 'api_key' in sanitized:
            sanitized['api_key'] = '***'
        return sanitized
    
    def _normalize_review(
        self,
        raw_data: Dict[str, Any],
        brand: str,
        app_identifier: str
    ) -> Review:
        """
        Abstract method - must be implemented by subclasses.
        
        Each platform has different response structure.
        """
        raise NotImplementedError("Subclass must implement _normalize_review()")

