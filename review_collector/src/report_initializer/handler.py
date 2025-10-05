"""
Report Initializer Lambda Handler

Generates job_id and prepares parameters for parallel collection.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Initialize report generation job.
    
    Input:
    {
        "brand": "telegram",
        "sources": {
            "appstore": "544007664",
            "googleplay": "org.telegram.messenger",
            "trustpilot": "telegram.org"
        },
        "limit": 50,
        "processing_endpoint_url": "https://your-api.com/process"
    }
    
    Output:
    {
        "job_id": "job_20251004_123456_abc123de",
        "brand": "telegram",
        "sources": {...},
        "limit": 50,
        "processing_endpoint_url": "https://your-api.com/process",
        "timestamp": "2025-10-04T12:00:00.000Z"
    }
    """
    logger.info("=" * 60)
    logger.info("🚀 Report Initializer Started")
    logger.info("=" * 60)
    logger.info(f"Event: {json.dumps(event, default=str)}")
    
    try:
        # Validate required fields
        brand = event.get('brand')
        if not brand:
            raise ValueError("Field 'brand' is required")
        
        sources = event.get('sources', {})
        if not sources:
            raise ValueError("Field 'sources' is required and must not be empty")
        
        # Normalize sources - ensure all keys exist (empty string if not provided)
        normalized_sources = {
            'appstore': sources.get('appstore', ''),
            'googleplay': sources.get('googleplay', ''),
            'trustpilot': sources.get('trustpilot', '')
        }
        
        # Optional fields
        processing_endpoint_url = event.get('processing_endpoint_url', 'https://webhook.site/test-endpoint')
        include_news = event.get('include_news', True)
        reddit_keywords = event.get('reddit_keywords', '')  # Reddit search keywords
        limit = event.get('limit', 50)
        
        # Validate limit
        if not isinstance(limit, int) or limit < 1 or limit > 500:
            raise ValueError("Field 'limit' must be an integer between 1 and 500")
        
        # Generate unique job_id
        timestamp = datetime.utcnow()
        job_id = f"job_{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"✅ Generated job_id: {job_id}")
        logger.info(f"   Brand: {brand}")
        logger.info(f"   Sources: {[k for k, v in normalized_sources.items() if v]}")
        logger.info(f"   Limit: {limit}")
        
        # Prepare output
        result = {
            'job_id': job_id,
            'brand': brand,
            'sources': normalized_sources,  # Use normalized sources with all keys
            'reddit_keywords': reddit_keywords,  # Pass reddit keywords
            'limit': limit,
            'include_news': include_news,
            'endpoint_url': processing_endpoint_url,  # Renamed for consistency
            'timestamp': timestamp.isoformat() + 'Z'
        }
        
        logger.info("✅ Initialization completed successfully")
        return result
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}", exc_info=True)
        raise

