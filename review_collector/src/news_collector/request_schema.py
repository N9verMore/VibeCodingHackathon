"""
Request/Response Schema for News Collector Lambda

Handles validation and parsing of Lambda events.
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import date


@dataclass
class CollectNewsRequest:
    """
    Request schema for news collection.
    
    Attributes:
        brand: Search term/keyword (e.g., 'Tesla', 'Apple')
        limit: Max number of articles to collect (1-500)
        search_type: 'everything' or 'top-headlines'
        from_date: Start date (everything only)
        to_date: End date (everything only)
        language: Language code (everything only)
        country: Country code (top-headlines only)
        category: News category (top-headlines only)
        sources: Comma-separated source IDs (top-headlines only)
    """
    
    brand: str
    limit: int = 100
    search_type: str = "everything"
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    language: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    sources: Optional[str] = None
    search_in: Optional[str] = None  # title, description, content
    
    def __post_init__(self):
        """Validate request parameters"""
        self._validate()
    
    def _validate(self):
        """Validate all fields"""
        if not self.brand:
            raise ValueError("'brand' is required")
        
        if not isinstance(self.limit, int) or not 1 <= self.limit <= 500:
            raise ValueError("'limit' must be an integer between 1 and 500")
        
        if self.search_type not in ["everything", "top-headlines"]:
            raise ValueError("'search_type' must be 'everything' or 'top-headlines'")
        
        # Validate top-headlines constraints
        if self.search_type == "top-headlines":
            if self.sources and (self.country or self.category):
                raise ValueError("Cannot use 'sources' with 'country' or 'category'")
            
            if self.category and self.category not in [
                "business", "entertainment", "general", "health", "science", "sports", "technology"
            ]:
                raise ValueError(f"Invalid category: {self.category}")
        
        # Validate search_in
        if self.search_in and self.search_in not in ["title", "description", "content"]:
            raise ValueError(f"Invalid search_in: {self.search_in}. Must be 'title', 'description', or 'content'")
        
        # Validate dates
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValueError("'from_date' cannot be after 'to_date'")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'brand': self.brand,
            'limit': self.limit,
            'search_type': self.search_type,
        }
        
        if self.from_date:
            result['from_date'] = self.from_date.isoformat()
        if self.to_date:
            result['to_date'] = self.to_date.isoformat()
        if self.language:
            result['language'] = self.language
        if self.country:
            result['country'] = self.country
        if self.category:
            result['category'] = self.category
        if self.sources:
            result['sources'] = self.sources
        if self.search_in:
            result['search_in'] = self.search_in
        
        return result


@dataclass
class CollectNewsResponse:
    """Response schema for news collection"""
    
    success: bool
    message: str
    statistics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'success': self.success,
            'message': self.message,
        }
        
        if self.statistics:
            result['statistics'] = self.statistics
        if self.error:
            result['error'] = self.error
        if self.request:
            result['request'] = self.request
        
        return result
    
    @classmethod
    def success_response(
        cls,
        message: str,
        statistics: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> 'CollectNewsResponse':
        """Create success response"""
        return cls(
            success=True,
            message=message,
            statistics=statistics,
            request=request_data
        )
    
    @classmethod
    def error_response(
        cls,
        error: str,
        message: str,
        request_data: Dict[str, Any]
    ) -> 'CollectNewsResponse':
        """Create error response"""
        return cls(
            success=False,
            message=message,
            error=error,
            request=request_data
        )


def parse_lambda_event(event: Dict[str, Any]) -> CollectNewsRequest:
    """
    Parse Lambda event into CollectNewsRequest.
    
    Supports both API Gateway and direct invocation formats.
    
    Args:
        event: Lambda event dict
        
    Returns:
        Validated CollectNewsRequest
        
    Raises:
        ValueError: If validation fails
    """
    # Check if this is an API Gateway event
    if 'body' in event:
        # API Gateway POST request
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
    else:
        # Direct Lambda invocation
        body = event
    
    # Parse dates
    from_date = None
    to_date = None
    
    if 'from_date' in body:
        from_date = date.fromisoformat(body['from_date'])
    if 'to_date' in body:
        to_date = date.fromisoformat(body['to_date'])
    
    return CollectNewsRequest(
        brand=body.get('brand', ''),
        limit=body.get('limit', 100),
        search_type=body.get('search_type', 'everything'),
        from_date=from_date,
        to_date=to_date,
        language=body.get('language'),
        country=body.get('country'),
        category=body.get('category'),
        sources=body.get('sources'),
        search_in=body.get('search_in')
    )


def format_lambda_response(status_code: int, response: CollectNewsResponse) -> Dict[str, Any]:
    """
    Format response for Lambda/API Gateway.
    
    Args:
        status_code: HTTP status code
        response: CollectNewsResponse object
        
    Returns:
        Lambda response dict
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(response.to_dict(), indent=2, default=str)
    }

