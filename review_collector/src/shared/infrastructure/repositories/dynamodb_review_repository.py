"""
DynamoDB Review Repository - Infrastructure Adapter

Implements ReviewRepository port using AWS DynamoDB.
Provides idempotent save operations.
"""

import os
import logging
from typing import Optional, List
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

from domain import Review, ReviewRepository, ReviewSource


logger = logging.getLogger(__name__)


class DynamoDBReviewRepository(ReviewRepository):
    """
    DynamoDB implementation of ReviewRepository.
    
    Table schema:
        PK: source#id (String) - Partition key
        Attributes: all Review fields
        GSI: brand-created_at-index for querying by brand
    """
    
    def __init__(self, table_name: Optional[str] = None):
        """
        Initialize repository.
        
        Args:
            table_name: DynamoDB table name (defaults to env var TABLE_NAME)
        """
        self.table_name = table_name or os.environ.get('TABLE_NAME', 'ReviewsTable')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"Initialized DynamoDB repository with table: {self.table_name}")
    
    def save(self, review: Review) -> bool:
        """
        Save review with idempotency check.
        
        Only writes if:
        - Review doesn't exist, OR
        - Review exists but content_hash differs
        
        Returns:
            True if written, False if skipped
        """
        pk = f"{review.source.value}#{review.id}"
        
        # Check if review exists
        existing = self.get_by_id(review.source.value, review.id)
        
        if existing and existing.content_hash == review.content_hash:
            logger.info(f"Review {pk} unchanged, skipping write")
            return False
        
        # Convert to DynamoDB item
        item = review.to_dynamodb_item()
        
        try:
            self.table.put_item(Item=item)
            logger.info(f"Saved review {pk} (brand: {review.brand}, rating: {review.rating})")
            return True
        except ClientError as e:
            logger.error(f"Failed to save review {pk}: {e}")
            raise
    
    def get_by_id(self, source: str, review_id: str) -> Optional[Review]:
        """
        Retrieve review by composite key.
        
        Args:
            source: Review source (appstore/googleplay/trustpilot)
            review_id: Review ID from platform
            
        Returns:
            Review if found, None otherwise
        """
        pk = f"{source}#{review_id}"
        
        try:
            response = self.table.get_item(Key={'pk': pk})
            
            if 'Item' not in response:
                return None
            
            return Review.from_dynamodb_item(response['Item'])
        
        except ClientError as e:
            logger.error(f"Failed to get review {pk}: {e}")
            raise
    
    def get_by_brand(self, brand: str, limit: int = 100) -> List[Review]:
        """
        Query reviews by brand using GSI.
        
        Args:
            brand: Brand identifier
            limit: Maximum number of results
            
        Returns:
            List of reviews sorted by created_at descending
        """
        try:
            response = self.table.query(
                IndexName='brand-created_at-index',
                KeyConditionExpression='brand = :brand',
                ExpressionAttributeValues={':brand': brand},
                ScanIndexForward=False,  # Descending order
                Limit=limit
            )
            
            reviews = [
                Review.from_dynamodb_item(item)
                for item in response.get('Items', [])
            ]
            
            logger.info(f"Retrieved {len(reviews)} reviews for brand {brand}")
            return reviews
        
        except ClientError as e:
            logger.error(f"Failed to query reviews for brand {brand}: {e}")
            raise
    
    def batch_save(self, reviews: List[Review]) -> dict:
        """
        Save multiple reviews in batch (with idempotency).
        
        Args:
            reviews: List of reviews to save
            
        Returns:
            Statistics dict with counts
        """
        stats = {'written': 0, 'skipped': 0, 'errors': 0}
        
        for review in reviews:
            try:
                if self.save(review):
                    stats['written'] += 1
                else:
                    stats['skipped'] += 1
            except Exception as e:
                logger.error(f"Error saving review {review.id}: {e}")
                stats['errors'] += 1
        
        logger.info(f"Batch save complete: {stats}")
        return stats

