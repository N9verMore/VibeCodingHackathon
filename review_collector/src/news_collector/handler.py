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


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    🎯 Lambda handler for news collection from NewsAPI.
    
    Supports 2 invocation methods:
    
    1️⃣ API Gateway (HTTP POST)
    ---------------------------
    POST /collect-news
    {
        "brand": "Tesla",
        "limit": 50,
        "search_type": "everything",
        "from_date": "2025-10-01",
        "language": "en"
    }
    
    2️⃣ Direct Lambda Invoke
    ------------------------
    aws lambda invoke --function-name news-collector-lambda \
      --payload '{"brand":"Tesla","limit":50}'
    
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
        # 🔍 Parse and validate request
        request = parse_lambda_event(event)
        logger.info(f"✅ Parsed request: {request.to_dict()}")
        
        # 🚀 Execute collection
        stats = _collect_news(request)
        
        # 📊 Format success response
        response = CollectNewsResponse.success_response(
            message='News articles collected successfully',
            statistics=stats,
            request_data=request.to_dict()
        )
        
        logger.info("=" * 60)
        logger.info("✅ Lambda execution completed successfully")
        logger.info("=" * 60)
        
        return format_lambda_response(200, response)
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        response = CollectNewsResponse.error_response(
            error='ValidationError',
            message=str(e),
            request_data=event if isinstance(event, dict) else {}
        )
        return format_lambda_response(400, response)
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}", exc_info=True)
        response = CollectNewsResponse.error_response(
            error='InternalServerError',
            message=str(e),
            request_data=event if isinstance(event, dict) else {}
        )
        return format_lambda_response(500, response)


def _collect_news(request: CollectNewsRequest) -> Dict[str, Any]:
    """
    Execute news collection workflow.
    
    Args:
        request: Validated CollectNewsRequest
        
    Returns:
        Statistics dictionary
    """
    logger.info(f"🎯 Collecting news for brand: {request.brand}")
    logger.info(f"   Search type: {request.search_type}")
    logger.info(f"   Limit: {request.limit}")
    
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
    
    # Initialize repository
    repository = NewsArticleRepository()
    logger.info("✅ Initialized NewsArticle repository")
    
    # Execute use case
    use_case = CollectNewsUseCase(api_client, repository)
    
    logger.info("🚀 Starting collection workflow...")
    stats = use_case.execute(
        brand=request.brand,
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

