"""
News Collector Lambda Handler

Entry point for collecting news articles from NewsAPI.
Independent from review collection - separate Lambda function.
"""

import os
import json
import logging
import sys
from typing import Dict, Any

# Add shared layer to path
sys.path.insert(0, '/opt/python')

from newsapi_client import NewsAPIClient
from news_repository import NewsArticleRepository
from collect_news_use_case import CollectNewsUseCase
from request_schema import (
    CollectNewsRequest,
    CollectNewsResponse,
    parse_lambda_event,
    format_lambda_response
)

# Import from Lambda Layer (shared infrastructure)
from infrastructure.clients.secrets_client import SecretsClient
from utils.brand_normalizer import normalize_brand_for_storage, normalize_brand_for_search


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    🎯 Lambda handler for news collection from NewsAPI.
    
    Supports 3 invocation methods:
    
    1️⃣ API Gateway (HTTP POST)
    ---------------------------
    POST /collect-news
    {
        "brand": "Tesla",
        "limit": 50,
        "search_type": "everything",
        "from_date": "2025-10-01",
        "language": "en",
        "job_id": "job_20251004_abc123" (optional)
    }
    
    2️⃣ Direct Lambda Invoke
    ------------------------
    aws lambda invoke --function-name news-collector-lambda \
      --payload '{"brand":"Tesla","limit":50}'
    
    3️⃣ Step Functions Invoke (NEW)
    -------------------------------
    Called from Step Functions with job_id for orchestration
    
    Args:
        event: Event data (format depends on invocation method)
        context: Lambda context object
        
    Returns:
        Response with collection statistics
    """
    logger.info("=" * 60)
    logger.info("🗞️  News Collector Lambda Started")
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
        
        # 🚀 Execute collection
        stats = _collect_news(request, job_id=job_id)
        
        # 📊 Format success response
        response_data = {
            'success': True,
            'message': 'News articles collected successfully',
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


def _collect_news(request: CollectNewsRequest, job_id: str = None) -> Dict[str, Any]:
    """
    Execute news collection workflow.
    
    Args:
        request: Validated CollectNewsRequest
        job_id: Optional job identifier for grouping news articles
        
    Returns:
        Statistics dictionary
    """
    # Normalize brand names
    brand_for_storage = normalize_brand_for_storage(request.brand)
    brand_for_search = normalize_brand_for_search(request.brand)
    
    logger.info(f"🎯 Collecting news for brand: {request.brand}")
    logger.info(f"   Brand for search: {brand_for_search}")
    logger.info(f"   Brand for storage: {brand_for_storage}")
    logger.info(f"   Search type: {request.search_type}")
    logger.info(f"   Limit: {request.limit}")
    if job_id:
        logger.info(f"   Job ID: {job_id}")
    
    # Get NewsAPI credentials from Secrets Manager
    logger.info("🔐 Retrieving NewsAPI credentials...")
    secrets_client = SecretsClient()
    newsapi_key = secrets_client.get_newsapi_key()
    
    if not newsapi_key:
        raise ValueError("NewsAPI key not found in Secrets Manager")
    
    logger.info("✅ Retrieved NewsAPI credentials")
    
    # Initialize NewsAPI client
    api_client = NewsAPIClient(newsapi_key)
    logger.info("✅ Initialized NewsAPI client")
    
    # Initialize repository with job_id support
    repository = NewsArticleRepository(job_id=job_id)
    logger.info("✅ Initialized NewsArticle repository")
    
    # Execute use case
    use_case = CollectNewsUseCase(api_client, repository)
    
    logger.info("🚀 Starting collection workflow...")
    # Pass both brand names: search for API, storage for DB
    stats = use_case.execute(
        brand=brand_for_search,  # Use Title Case with spaces for API search
        brand_for_storage=brand_for_storage,  # Use lowercase with underscores for DB
        limit=request.limit,
        search_type=request.search_type,
        from_date=request.from_date,
        to_date=request.to_date,
        language=request.language,
        country=request.country,
        category=request.category,
        sources=request.sources,
        search_in=request.search_in
    )
    
    logger.info(f"📊 Collection statistics: {stats}")
    
    return stats

