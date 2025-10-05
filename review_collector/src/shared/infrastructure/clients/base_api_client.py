"""
Base API Client

Abstract base class for all API clients with common functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from domain import Review


logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """
    Abstract base class for API clients.
    
    Provides:
    - HTTP session with retry logic
    - Rate limiting support
    - Common error handling
    - Pagination interface
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize API client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = self._create_session()
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with retry strategy.
        
        Returns:
            Configured requests Session
        """
        session = requests.Session()
        
        # Retry strategy: 3 retries with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> None:
        """
        Authenticate with API using provided credentials.
        
        Args:
            credentials: API credentials from Secrets Manager
        """
        pass
    
    @abstractmethod
    def fetch_reviews(
        self,
        app_identifier: str,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
        brand: str = ''
    ) -> List[Review]:
        """
        Fetch reviews from API.
        
        Args:
            app_identifier: App/business identifier
            since: Fetch reviews created after this timestamp
            limit: Maximum number of reviews to fetch
            
        Returns:
            List of normalized Review entities
        """
        pass
    
    @abstractmethod
    def _normalize_review(self, raw_data: Dict[str, Any], brand: str, app_identifier: str) -> Review:
        """
        Normalize platform-specific review data to Review entity.
        
        Args:
            raw_data: Raw review data from API
            brand: Brand identifier
            app_identifier: App identifier
            
        Returns:
            Normalized Review entity
        """
        pass
    
    def _handle_pagination(
        self,
        url: str,
        headers: Dict[str, str],
        params: Dict[str, Any],
        data_key: str,
        next_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generic pagination handler.
        
        Args:
            url: API endpoint URL
            headers: Request headers
            params: Query parameters
            data_key: Key in response containing data array
            next_key: Key in response containing next page token/cursor
            
        Returns:
            List of all items from paginated responses
        """
        all_items = []
        
        while True:
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract items
                items = data.get(data_key, [])
                all_items.extend(items)
                
                logger.info(f"Fetched {len(items)} items, total: {len(all_items)}")
                
                # Check for next page
                if next_key and data.get(next_key):
                    params['next'] = data[next_key]
                else:
                    break
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                raise
        
        return all_items
    
    def close(self):
        """Close HTTP session"""
        if self.session:
            self.session.close()
            logger.info(f"Closed {self.__class__.__name__} session")

