"""
Reddit Collector Lambda Handler

Entry point for collecting Reddit posts mentioning brands.
Maps posts to Review entities and stores in DynamoDB.
"""

import os
import json
import logging
import sys
from typing import Dict, Any

# Add shared layer to path
sys.path.insert(0, '/opt/python')

from reddit_client import RedditClient
from reddit_mapper import map_reddit_post_to_review
from request_schema import (
    CollectRedditRequest,
    parse_lambda_event,
    format_lambda_response
)

# Import from Lambda Layer (shared infrastructure)
from infrastructure.repositories.dynamodb_review_repository import DynamoDBReviewRepository
from infrastructure.clients.secrets_client import SecretsClient
from utils.brand_normalizer import normalize_brand_for_storage


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    🎯 Lambda handler for Reddit post collection.
    
    Supports 3 invocation methods:
    
    1️⃣ API Gateway (HTTP POST)
    ---------------------------
    POST /collect-reddit
    {
        "brand": "Flo",
        "keywords": "Flo app",
        "limit": 100,
        "days_back": 30,
        "sort": "new",
        "job_id": "job_20251004_abc123" (optional)
    }
    
    2️⃣ Direct Lambda Invoke
    ------------------------
    aws lambda invoke --function-name reddit-collector-lambda \
      --payload '{"brand":"Flo","keywords":"Flo app","limit":100}'
    
    3️⃣ Step Functions Invoke
    -------------------------------
    Called from Step Functions with job_id for orchestration
    
    Args:
        event: Event data (format depends on invocation method)
        context: Lambda context object
        
    Returns:
        Response with collection statistics
    """
    logger.info("=" * 60)
    logger.info("🗣️  Reddit Collector Lambda Started")
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
        stats = _collect_reddit_posts(request, job_id=job_id)
        
        # 📊 Format success response
        response_data = {
            'success': True,
            'message': 'Reddit posts collected successfully',
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


def _collect_reddit_posts(request: CollectRedditRequest, job_id: str = None) -> Dict[str, Any]:
    """
    Execute Reddit post collection workflow.
    
    Args:
        request: Validated CollectRedditRequest
        job_id: Optional job identifier for grouping posts
        
    Returns:
        Statistics dictionary
    """
    # Normalize brand names
    brand_for_storage = normalize_brand_for_storage(request.brand)
    
    logger.info(f"🎯 Collecting Reddit posts for brand: {request.brand}")
    logger.info(f"   Brand for storage: {brand_for_storage}")
    logger.info(f"   Keywords: {request.keywords}")
    logger.info(f"   Limit: {request.limit}")
    logger.info(f"   Days back: {request.days_back}")
    logger.info(f"   Sort: {request.sort}")
    if job_id:
        logger.info(f"   Job ID: {job_id}")
    
    # Get Reddit credentials from Secrets Manager
    logger.info("🔐 Retrieving Reddit credentials...")
    secrets_client = SecretsClient()
    reddit_creds = secrets_client.get_reddit_credentials()
    
    if not reddit_creds:
        raise ValueError("Reddit credentials not found in Secrets Manager")
    
    logger.info("✅ Retrieved Reddit credentials")
    
    # Initialize Reddit client
    reddit_client = RedditClient(
        client_id=reddit_creds['client_id'],
        client_secret=reddit_creds['client_secret'],
        user_agent=reddit_creds.get('user_agent', 'Brand Monitor v1.0')
    )
    logger.info("✅ Initialized Reddit client")
    
    # Search for posts
    logger.info("🔍 Searching Reddit...")
    posts = reddit_client.search_posts(
        keywords=request.keywords,
        limit=request.limit,
        days_back=request.days_back,
        sort=request.sort
    )
    
    logger.info(f"📊 Found {len(posts)} posts")
    
    # Map posts to Review entities
    logger.info("🔄 Mapping posts to Review entities...")
    reviews = []
    for post in posts:
        try:
            review = map_reddit_post_to_review(post, brand_for_storage)
            reviews.append(review)
        except Exception as e:
            logger.warning(f"Failed to map post {post.get('id')}: {e}")
    
    logger.info(f"✅ Mapped {len(reviews)} reviews")
    
    # Initialize repository with job_id support
    repository = DynamoDBReviewRepository(job_id=job_id)
    logger.info("✅ Initialized DynamoDB repository")
    
    # Save reviews to DynamoDB
    logger.info("💾 Saving reviews to DynamoDB...")
    stats = {
        'fetched': len(posts),
        'mapped': len(reviews),
        'saved': 0,
        'skipped': 0,
        'errors': []
    }
    
    for review in reviews:
        try:
            repository.save(review)
            stats['saved'] += 1
        except Exception as e:
            logger.warning(f"Failed to save review {review.id}: {e}")
            stats['skipped'] += 1
            stats['errors'].append({
                'id': review.id,
                'error': str(e)
            })
    
    logger.info(f"📊 Collection statistics: {stats}")
    
    # Remove detailed errors from response (keep count only)
    if stats['errors']:
        error_count = len(stats['errors'])
        stats['errors'] = f"{error_count} errors occurred"
    else:
        stats.pop('errors')
    
    return stats

