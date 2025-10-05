"""
ReviewRepository Port (Interface)

Defines the contract for review persistence without knowing implementation details.
This is the "port" in hexagonal architecture - adapters will implement this.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from .review import Review


class ReviewRepository(ABC):
    """
    Abstract interface for review storage.
    
    Implementations (adapters) must provide idempotent save operations.
    """
    
    @abstractmethod
    def save(self, review: Review) -> bool:
        """
        Save review to storage with idempotency.
        
        Should only write if:
        - Review doesn't exist, OR
        - Review exists but content_hash has changed
        
        Args:
            review: Review entity to save
            
        Returns:
            True if review was written, False if skipped (no changes)
        """
        pass
    
    @abstractmethod
    def get_by_id(self, source: str, review_id: str) -> Optional[Review]:
        """
        Retrieve review by source and ID.
        
        Args:
            source: Review source (appstore/googleplay/trustpilot)
            review_id: Unique ID from source platform
            
        Returns:
            Review if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_brand(self, brand: str, limit: int = 100) -> List[Review]:
        """
        Get recent reviews for a brand.
        
        Args:
            brand: Brand identifier
            limit: Maximum number of reviews to return
            
        Returns:
            List of reviews sorted by created_at descending
        """
        pass

