"""
Unified Review Collector Lambda Handler

Entry point for collecting reviews from any app via SerpAPI.
Supports multiple invocation methods:
- API Gateway (HTTP POST)
- Direct Lambda Invoke (AWS CLI/SDK/Console)
"""

import os
import json
import logging
from typing import Dict, Any

from serpapi_appstore_client import SerpAPIAppStoreClient
from serpapi_googleplay_client import SerpAPIGooglePlayClient
from serpapi_trustpilot_client import SerpAPITrustpilotClient

# Import from Lambda Layer (located in /opt/python/)
from application.collect_reviews_use_case import CollectReviewsUseCase
from infrastructure.repositories.dynamodb_review_repository import DynamoDBReviewRepository
from infrastructure.clients.secrets_client import SecretsClient


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    🎯 Unified Lambda handler for review collection via SerpAPI.
    
    Supports 2 invocation methods:
    
    1️⃣ API Gateway (HTTP POST)
    ---------------------------
    POST /collect-reviews
    {
        "source": "appstore",
        "app_identifier": "544007664",
        "brand": "telegram",
        "limit": 100
    }
    
    2️⃣ Direct Lambda Invoke
    ------------------------
    aws lambda invoke --function-name serpapi-collector-lambda \
      --payload '{"source":"appstore","app_identifier":"544007664","brand":"telegram"}'
    
    Args:
        event: Event data (format depends on invocation method)
        context: Lambda context object
        
    Returns:
        Response with statistics and status
    """
    logger.info("=" * 60)
    logger.info("Unified Review Collector Lambda Started")
    logger.info("=" * 60)
    logger.info(f"Event: {json.dumps(event, default=str)}")
    
    try:
        # 🔍 Parse event and extract parameters
        params = _parse_event(event)
        logger.info(f"Parsed parameters: {params}")
        
        # ✅ Validate required fields
        _validate_params(params)
        
        # 🚀 Execute collection
        stats = _collect_reviews(params)
        
        # 📊 Format success response
        response = _format_response(200, {
            'success': True,
            'message': 'Reviews collected successfully',
            'statistics': stats,
            'input': {
                'source': params['source'],
                'app_identifier': params['app_identifier'],
                'brand': params['brand'],
                'limit': params.get('limit', 100)
            }
        })
        
        logger.info("=" * 60)
        logger.info("Lambda execution completed successfully")
        logger.info("=" * 60)
        
        return response
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        return _format_response(400, {
            'success': False,
            'error': 'Validation error',
            'message': str(e)
        })
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}", exc_info=True)
        return _format_response(500, {
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        })


def _parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse event and extract parameters based on invocation method.
    
    Args:
        event: Raw Lambda event
        
    Returns:
        Parsed parameters dictionary
    """
    # Method 1: API Gateway (has 'httpMethod' or 'body' field)
    if 'httpMethod' in event or 'body' in event:
        logger.info("📡 Invocation method: API Gateway")
        body_str = event.get('body', '{}')
        
        # Handle both string and dict body
        if isinstance(body_str, str):
            params = json.loads(body_str)
        else:
            params = body_str
            
        return params
    
    # Method 2: Direct Lambda Invoke
    else:
        logger.info("⚡ Invocation method: Direct Invoke")
        return event


def _validate_params(params: Dict[str, Any]) -> None:
    """
    Validate required parameters.
    
    Args:
        params: Parameters dictionary
        
    Raises:
        ValueError: If validation fails
    """
    # Required fields
    required_fields = ['source', 'app_identifier', 'brand']
    
    for field in required_fields:
        if field not in params or not params[field]:
            raise ValueError(f"Missing required field: '{field}'")
    
    # Validate source
    valid_sources = ['appstore', 'googleplay', 'trustpilot']
    source = params['source'].lower()
    
    if source not in valid_sources:
        raise ValueError(
            f"Invalid source: '{source}'. "
            f"Must be one of: {', '.join(valid_sources)}"
        )
    
    # Validate limit (optional)
    if 'limit' in params:
        limit = params['limit']
        if not isinstance(limit, int) or limit < 1 or limit > 500:
            raise ValueError("'limit' must be an integer between 1 and 500")
    
    logger.info("✅ Parameters validated successfully")


def _collect_reviews(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute review collection workflow.
    
    Args:
        params: Validated parameters
        
    Returns:
        Statistics dictionary
    """
    source = params['source'].lower()
    app_identifier = params['app_identifier']
    brand = params['brand']
    limit = params.get('limit', 100)
    
    logger.info(f"🎯 Collecting reviews from {source} for {brand} (app: {app_identifier})")
    
    # Get SerpAPI key from Secrets Manager
    logger.info("🔐 Retrieving SerpAPI credentials...")
    secrets_client = SecretsClient()
    serpapi_key = secrets_client.get_serpapi_key()
    
    if not serpapi_key:
        raise ValueError("SerpAPI key not found in Secrets Manager")
    
    logger.info("✅ SerpAPI credentials retrieved")
    
    # Select appropriate SerpAPI client
    clients = {
        'appstore': SerpAPIAppStoreClient(serpapi_key),
        'googleplay': SerpAPIGooglePlayClient(serpapi_key),
        'trustpilot': SerpAPITrustpilotClient(serpapi_key)
    }
    
    api_client = clients[source]
    logger.info(f"✅ Initialized {api_client.__class__.__name__}")
    
    # Initialize repository
    repository = DynamoDBReviewRepository()
    logger.info("✅ Initialized DynamoDB repository")
    
    # Execute use case
    use_case = CollectReviewsUseCase(api_client, repository)
    
    logger.info("🚀 Starting collection workflow...")
    stats = use_case.execute(
        credentials={},  # SerpAPI key already in client
        app_identifier=app_identifier,
        brand=brand,
        since=None,
        limit=limit
    )
    
    logger.info(f"📊 Collection statistics: {stats}")
    
    return stats


def _format_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Lambda response for different invocation methods.
    
    Args:
        status_code: HTTP status code
        body: Response body
        
    Returns:
        Formatted response dictionary
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body, default=str, ensure_ascii=False)
    }

