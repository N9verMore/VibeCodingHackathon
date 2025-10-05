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
from dataforseo_trustpilot_client import DataForSEOTrustpilotClient
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
from utils.brand_normalizer import normalize_brand_for_storage


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    🎯 Unified Lambda handler for review collection via SerpAPI/DataForSEO.
    
    For Trustpilot (DataForSEO): Returns 202 Accepted immediately after task creation
    For other sources (SerpAPI): Returns 200 OK with results
    
    Supports 3 invocation methods:
    
    1️⃣ API Gateway (HTTP POST)
    ---------------------------
    POST /collect-reviews
    {
        "source": "trustpilot",
        "app_identifier": "www.zara.com",
        "brand": "zara",
        "limit": 40,
        "job_id": "job_20251004_abc123" (optional)
    }
    
    2️⃣ Direct Lambda Invoke
    ------------------------
    aws lambda invoke --function-name serpapi-collector-lambda \
      --payload '{"source":"trustpilot","app_identifier":"www.zara.com","brand":"zara"}'
    
    3️⃣ Step Functions Invoke (NEW)
    -------------------------------
    Called from Step Functions with job_id for orchestration
    
    Args:
        event: Event data (format depends on invocation method)
        context: Lambda context object
        
    Returns:
        Response with task info or statistics
    """
    logger.info("=" * 60)
    logger.info("🚀 Unified Review Collector Lambda Started")
    logger.info("=" * 60)
    logger.info(f"Event: {json.dumps(event, default=str)}")
    
    try:
        # Extract job_id if provided (for Step Functions orchestration)
        job_id = event.get('job_id') if isinstance(event, dict) else None
        if job_id:
            logger.info(f"🔖 Job ID: {job_id}")
        
        # 🔍 Parse and validate request
        request = parse_lambda_event(event)
        logger.info(f"✅ Parsed request: {request.to_dict()}")
        
        # Skip if app_identifier is empty (source not provided in original request)
        if not request.app_identifier or request.app_identifier.strip() == '':
            logger.info(f"⏭️  Skipping {request.source} - no app_identifier provided")
            return format_lambda_response(200, {
                'success': True,
                'message': f'{request.source} skipped - not requested',
                'statistics': {'fetched': 0, 'saved': 0, 'skipped': 0},
                'request': request.to_dict()
            })
        
        # 🚀 Execute collection (sync for all sources)
        stats = _collect_reviews(request, job_id=job_id)
        
        # 📊 Format success response
        response_data = {
            'success': True,
            'message': 'Reviews collected successfully',
            'statistics': stats,
            'request': request.to_dict()
        }
        
        # Add job_id to response if provided
        if job_id:
            response_data['job_id'] = job_id
        
        logger.info("=" * 60)
        logger.info("✅ Lambda execution completed successfully")
        logger.info("=" * 60)
        
        return format_lambda_response(200, response_data)
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        error_response = {
            'success': False,
            'error': 'ValidationError',
            'message': str(e),
            'request': event if isinstance(event, dict) else {}
        }
        return format_lambda_response(400, error_response)
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}", exc_info=True)
        error_response = {
            'success': False,
            'error': 'InternalServerError',
            'message': str(e),
            'request': event if isinstance(event, dict) else {}
        }
        return format_lambda_response(500, error_response)


def _collect_reviews(request: CollectReviewsRequest, job_id: str = None) -> Dict[str, Any]:
    """
    Execute review collection workflow.
    
    Args:
        request: Validated CollectReviewsRequest
        job_id: Optional job identifier for grouping reviews
        
    Returns:
        Statistics dictionary
    """
    source = request.source
    app_identifier = request.app_identifier
    brand = request.brand
    limit = request.limit
    
    logger.info(f"🎯 Collecting reviews from {source} for {brand} (app: {app_identifier})")
    if job_id:
        logger.info(f"   Job ID: {job_id}")
    
    # Get API credentials from Secrets Manager
    logger.info("🔐 Retrieving API credentials...")
    secrets_client = SecretsClient()
    
    # Select appropriate API client based on source
    if source == 'trustpilot':
        # Use DataForSEO for Trustpilot
        logger.info("Using DataForSEO API for Trustpilot")
        dataforseo_creds = secrets_client.get_dataforseo_credentials()
        api_client = DataForSEOTrustpilotClient(
            login=dataforseo_creds['login'],
            password=dataforseo_creds['password']
        )
    else:
        # Use SerpAPI for App Store and Google Play
        logger.info(f"Using SerpAPI for {source}")
        serpapi_key = secrets_client.get_serpapi_key()
        
        if not serpapi_key:
            raise ValueError("SerpAPI key not found in Secrets Manager")
        
        clients = {
            'appstore': SerpAPIAppStoreClient(serpapi_key),
            'googleplay': SerpAPIGooglePlayClient(serpapi_key)
        }
        
        api_client = clients[source]
    
    logger.info(f"✅ Initialized {api_client.__class__.__name__}")
    
    # Normalize brand for storage (lowercase with underscores)
    normalized_brand = normalize_brand_for_storage(brand)
    logger.info(f"📝 Brand normalization: '{brand}' -> '{normalized_brand}'")
    
    # Initialize repository with job_id support
    repository = DynamoDBReviewRepository(job_id=job_id)
    logger.info("✅ Initialized DynamoDB repository")
    
    # Execute use case
    use_case = CollectReviewsUseCase(api_client, repository)
    
    logger.info("🚀 Starting collection workflow...")
    stats = use_case.execute(
        credentials={},  # API credentials already in client
        app_identifier=app_identifier,
        brand=normalized_brand,  # Use normalized brand for storage
        since=None,
        limit=limit
    )
    
    logger.info(f"📊 Collection statistics: {stats}")
    
    return stats

