"""
Request/Response Schemas for Reddit Collector Lambda

Handles request parsing and response formatting.
"""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class CollectRedditRequest:
    """
    Request schema for Reddit post collection.
    
    Attributes:
        brand: Brand name
        keywords: Keywords to search for in Reddit (e.g., "Flo app")
        limit: Maximum number of posts to collect
        days_back: How many days back to search
        sort: Sort order (new/hot/top/relevance)
        job_id: Optional job identifier for orchestration
    """
    brand: str
    keywords: str
    limit: int = 100
    days_back: int = 30
    sort: str = "new"
    job_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'brand': self.brand,
            'keywords': self.keywords,
            'limit': self.limit,
            'days_back': self.days_back,
            'sort': self.sort,
            'job_id': self.job_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollectRedditRequest':
        """Create from dictionary with validation"""
        # Required fields
        brand = data.get('brand')
        if not brand:
            raise ValueError("'brand' is required")
        
        keywords = data.get('keywords')
        if not keywords:
            raise ValueError("'keywords' is required")
        
        # Optional fields with defaults
        limit = int(data.get('limit', 100))
        if limit < 1 or limit > 1000:
            raise ValueError("'limit' must be between 1 and 1000")
        
        days_back = int(data.get('days_back', 30))
        if days_back < 1 or days_back > 365:
            raise ValueError("'days_back' must be between 1 and 365")
        
        sort = data.get('sort', 'new')
        if sort not in ['new', 'hot', 'top', 'relevance']:
            raise ValueError("'sort' must be one of: new, hot, top, relevance")
        
        job_id = data.get('job_id')
        
        return cls(
            brand=brand,
            keywords=keywords,
            limit=limit,
            days_back=days_back,
            sort=sort,
            job_id=job_id
        )


def parse_lambda_event(event: Dict[str, Any]) -> CollectRedditRequest:
    """
    Parse Lambda event into CollectRedditRequest.
    
    Handles three invocation methods:
    1. API Gateway (HTTP POST) - body is JSON string
    2. Direct Lambda invoke - event is dict
    3. Step Functions - event is dict
    
    Args:
        event: Lambda event dict
        
    Returns:
        Parsed and validated CollectRedditRequest
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Detect invocation method
    if 'body' in event:
        # API Gateway invocation
        logger.info("📥 API Gateway invocation detected")
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        return CollectRedditRequest.from_dict(body)
    else:
        # Direct invoke or Step Functions
        logger.info("📥 Direct/Step Functions invocation detected")
        return CollectRedditRequest.from_dict(event)


def format_lambda_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Lambda response for API Gateway.
    
    Args:
        status_code: HTTP status code
        body: Response body dict
        
    Returns:
        Lambda response dict with proper CORS headers
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }

