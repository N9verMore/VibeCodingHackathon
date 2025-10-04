"""
NewsArticle Repository - DynamoDB Adapter

Implements repository pattern for NewsArticle persistence.
Uses the same DynamoDB table as reviews but with 'news' source prefix.
"""

import os
import logging
from typing import Optional, List
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from news_article import NewsArticle


logger = logging.getLogger(__name__)


class NewsArticleRepository:
    """
    DynamoDB implementation for NewsArticle storage.
    
    Uses same table as ReviewsTable:
        PK: news#id (String) - Partition key
        GSI: brand-created_at-index for querying by brand
    """
    
    def __init__(self, table_name: Optional[str] = None, job_id: Optional[str] = None):
        """
        Initialize repository.
        
        Args:
            table_name: DynamoDB table name (defaults to env var TABLE_NAME)
            job_id: Optional job identifier for grouping news articles (for orchestration)
        """
        self.table_name = table_name or os.environ.get('TABLE_NAME', 'ReviewsTableV2')
        self.job_id = job_id
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"Initialized NewsArticle repository with table: {self.table_name}")
        if job_id:
            logger.info(f"  Job ID: {job_id}")
    
    def save(self, article: NewsArticle) -> bool:
        """
        Save article with idempotency check.
        
        Only writes if:
        - Article doesn't exist, OR
        - Article exists but content_hash differs
        
        Returns:
            True if written, False if skipped
        """
        pk = f"news#{article.id}"
        
        # Check if article exists
        existing = self.get_by_id(article.id)
        
        if existing and existing.content_hash == article.content_hash:
            logger.info(f"Article {pk} unchanged, skipping write")
            return False
        
        # Convert to DynamoDB item
        item = article.to_dynamodb_item()
        
        try:
            self.table.put_item(Item=item)
            logger.info(f"Saved article {pk} (brand: {article.brand}, source: {article.source_name})")
            return True
        except ClientError as e:
            logger.error(f"Failed to save article {pk}: {e}")
            raise
    
    def get_by_id(self, article_id: str) -> Optional[NewsArticle]:
        """
        Retrieve article by ID.
        
        Args:
            article_id: Article ID
            
        Returns:
            NewsArticle if found, None otherwise
        """
        pk = f"news#{article_id}"
        
        try:
            response = self.table.get_item(Key={'pk': pk})
            
            if 'Item' not in response:
                return None
            
            return NewsArticle.from_dynamodb_item(response['Item'])
        
        except ClientError as e:
            logger.error(f"Failed to get article {pk}: {e}")
            raise
    
    def get_by_brand(self, brand: str, limit: int = 100) -> List[NewsArticle]:
        """
        Query articles by brand using GSI.
        
        Args:
            brand: Brand/search term
            limit: Maximum number of results
            
        Returns:
            List of articles sorted by published_at descending
        """
        try:
            response = self.table.query(
                IndexName='brand-created_at-index',
                KeyConditionExpression='brand = :brand AND begins_with(#src, :news)',
                ExpressionAttributeNames={
                    '#src': 'source'
                },
                ExpressionAttributeValues={
                    ':brand': brand,
                    ':news': 'news'
                },
                ScanIndexForward=False,  # Descending order
                Limit=limit
            )
            
            articles = [
                NewsArticle.from_dynamodb_item(item)
                for item in response.get('Items', [])
            ]
            
            logger.info(f"Retrieved {len(articles)} articles for brand {brand}")
            return articles
        
        except ClientError as e:
            logger.error(f"Failed to query articles for brand {brand}: {e}")
            raise
    
    def batch_save(self, articles: List[NewsArticle]) -> dict:
        """
        Save multiple articles in batch (with idempotency).
        
        Args:
            articles: List of articles to save
            
        Returns:
            Statistics dict with counts
        """
        stats = {'written': 0, 'skipped': 0, 'errors': 0}
        
        for article in articles:
            try:
                if self.save(article):
                    stats['written'] += 1
                else:
                    stats['skipped'] += 1
            except Exception as e:
                logger.error(f"Error saving article {article.id}: {e}")
                stats['errors'] += 1
        
        logger.info(f"Batch save complete: {stats}")
        return stats

