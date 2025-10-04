"""
Request Schema for Review Collector Lambda

Unified request/response schema with validation.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class ReviewSource(str, Enum):
    """Supported review sources"""
    APP_STORE = "appstore"
    GOOGLE_PLAY = "googleplay"
    TRUSTPILOT = "trustpilot"


@dataclass
class CollectReviewsRequest:
    """
    Unified request schema for collecting reviews.
    
    Example API Gateway request:
    POST /collect-reviews
    {
        "source": "appstore",
        "app_identifier": "544007664",
        "brand": "telegram",
        "limit": 100,
        "country": "us"
    }
    
    Example Direct Invoke:
    {
        "source": "googleplay",
        "app_identifier": "org.telegram.messenger",
        "brand": "telegram",
        "limit": 50
    }
    
    Attributes:
        source: Review source platform (appstore/googleplay/trustpilot)
        app_identifier: Platform-specific app identifier:
            - App Store: Numeric ID (e.g., "544007664")
            - Google Play: Package name (e.g., "org.telegram.messenger")
            - Trustpilot: Domain (e.g., "telegram.org")
        brand: Brand/company identifier (used for filtering)
        limit: Maximum number of reviews to collect (default: 100, max: 500)
        country: Country code for region-specific reviews (default: "us")
        metadata: Optional metadata for tracking/debugging
    """
    
    source: str
    app_identifier: str
    brand: str
    limit: Optional[int] = 100
    country: Optional[str] = "us"
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize fields"""
        self.validate()
        self.normalize()
    
    def validate(self) -> None:
        """
        Validate request fields.
        
        Raises:
            ValueError: If validation fails
        """
        # Validate source
        try:
            self.source = self.source.lower()
            ReviewSource(self.source)
        except ValueError:
            valid_sources = [s.value for s in ReviewSource]
            raise ValueError(
                f"Invalid source: '{self.source}'. "
                f"Must be one of: {', '.join(valid_sources)}"
            )
        
        # Validate app_identifier
        if not self.app_identifier or not isinstance(self.app_identifier, str):
            raise ValueError("'app_identifier' must be a non-empty string")
        
        # Validate brand
        if not self.brand or not isinstance(self.brand, str):
            raise ValueError("'brand' must be a non-empty string")
        
        # Validate limit
        if self.limit is not None:
            if not isinstance(self.limit, int):
                raise ValueError("'limit' must be an integer")
            if self.limit < 1:
                raise ValueError("'limit' must be at least 1")
            if self.limit > 500:
                raise ValueError("'limit' cannot exceed 500")
        
        # Validate country
        if self.country and not isinstance(self.country, str):
            raise ValueError("'country' must be a string")
    
    def normalize(self) -> None:
        """Normalize fields to standard format"""
        self.source = self.source.lower()
        self.brand = self.brand.lower()
        self.app_identifier = self.app_identifier.strip()
        
        if self.country:
            self.country = self.country.lower()
        
        if self.limit is None:
            self.limit = 100
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollectReviewsRequest':
        """
        Create request from dictionary.
        
        Args:
            data: Request data dictionary
            
        Returns:
            CollectReviewsRequest instance
        """
        return cls(
            source=data.get('source', ''),
            app_identifier=data.get('app_identifier', ''),
            brand=data.get('brand', ''),
            limit=data.get('limit'),
            country=data.get('country', 'us'),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            'source': self.source,
            'app_identifier': self.app_identifier,
            'brand': self.brand,
            'limit': self.limit,
            'country': self.country,
            'metadata': self.metadata
        }


@dataclass
class CollectReviewsResponse:
    """
    Unified response schema for review collection.
    
    Example success response:
    {
        "success": true,
        "message": "Reviews collected successfully",
        "statistics": {
            "brand": "telegram",
            "app_identifier": "544007664",
            "fetched": 100,
            "saved": 95,
            "skipped": 5,
            "errors": 0,
            "duration_seconds": 12.5
        },
        "request": {
            "source": "appstore",
            "app_identifier": "544007664",
            "brand": "telegram",
            "limit": 100,
            "country": "us"
        }
    }
    
    Example error response:
    {
        "success": false,
        "error": "ValidationError",
        "message": "Invalid source: 'invalid'. Must be one of: appstore, googleplay, trustpilot",
        "request": {...}
    }
    """
    
    success: bool
    message: str
    statistics: Optional[Dict[str, Any]] = None
    request: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        result = {
            'success': self.success,
            'message': self.message
        }
        
        if self.statistics:
            result['statistics'] = self.statistics
        
        if self.request:
            result['request'] = self.request
        
        if self.error:
            result['error'] = self.error
        
        return result
    
    def to_json(self) -> str:
        """Convert response to JSON string"""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)
    
    @classmethod
    def success_response(
        cls,
        message: str,
        statistics: Dict[str, Any],
        request_data: Dict[str, Any]
    ) -> 'CollectReviewsResponse':
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
        request_data: Optional[Dict[str, Any]] = None
    ) -> 'CollectReviewsResponse':
        """Create error response"""
        return cls(
            success=False,
            message=message,
            error=error,
            request=request_data
        )


def parse_lambda_event(event: Dict[str, Any]) -> CollectReviewsRequest:
    """
    Parse Lambda event and extract request parameters.
    
    Supports multiple invocation methods:
    - API Gateway (HTTP POST with body)
    - Direct Lambda Invoke (direct JSON payload)
    
    Args:
        event: Lambda event data
        
    Returns:
        CollectReviewsRequest instance
        
    Raises:
        ValueError: If parsing or validation fails
    """
    # Method 1: API Gateway (has 'httpMethod' or 'body' field)
    if 'httpMethod' in event or 'body' in event:
        body_str = event.get('body', '{}')
        
        # Handle both string and dict body
        if isinstance(body_str, str):
            params = json.loads(body_str)
        else:
            params = body_str
    
    # Method 2: Direct Lambda Invoke
    else:
        params = event
    
    # Create and validate request
    return CollectReviewsRequest.from_dict(params)


def format_lambda_response(
    status_code: int,
    response: CollectReviewsResponse
) -> Dict[str, Any]:
    """
    Format response for Lambda/API Gateway.
    
    Args:
        status_code: HTTP status code
        response: CollectReviewsResponse instance
        
    Returns:
        Formatted Lambda response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': response.to_json()
    }

