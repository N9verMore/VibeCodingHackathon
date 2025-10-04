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
from request_schema import (
    CollectReviewsRequest,
    CollectReviewsResponse,
    parse_lambda_event,
    format_lambda_response
)

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
    logger.info("🚀 Unified Review Collector Lambda Started")
    logger.info("=" * 60)
    logger.info(f"Event: {json.dumps(event, default=str)}")
    
    try:
        # 🔍 Parse and validate request
        request = parse_lambda_event(event)
        logger.info(f"✅ Parsed request: {request.to_dict()}")
        
        # 🚀 Execute collection
        stats = _collect_reviews(request)
        
        # 📊 Format success response
        response = CollectReviewsResponse.success_response(
            message='Reviews collected successfully',
            statistics=stats,
            request_data=request.to_dict()
        )
        
        logger.info("=" * 60)
        logger.info("✅ Lambda execution completed successfully")
        logger.info("=" * 60)
        
        return format_lambda_response(200, response)
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        response = CollectReviewsResponse.error_response(
            error='ValidationError',
            message=str(e),
            request_data=event if isinstance(event, dict) else {}
        )
        return format_lambda_response(400, response)
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}", exc_info=True)
        response = CollectReviewsResponse.error_response(
            error='InternalServerError',
            message=str(e),
            request_data=event if isinstance(event, dict) else {}
        )
        return format_lambda_response(500, response)


def _collect_reviews(request: CollectReviewsRequest) -> Dict[str, Any]:
    """
    Execute review collection workflow.
    
    Args:
        request: Validated CollectReviewsRequest
        
    Returns:
        Statistics dictionary
    """
    source = request.source
    app_identifier = request.app_identifier
    brand = request.brand
    limit = request.limit
    
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

