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
        "appstore": {
            "id": "544007664",
            "country": "us"
        },
        "googleplay": {
            "package_name": "org.telegram.messenger",
            "country": "us"
        },
        "trustpilot": {
            "domain": "telegram.org"
        },
        "reddit": {
            "keywords": "telegram app",
            "days_back": 30,
            "sort": "new"
        },
        "news": {
            "keywords": "Telegram",
            "search_type": "everything",
            "from_date": "2024-10-01",
            "to_date": "2024-10-04",
            "language": "en"
        },
        "limit": 50,
        "processing_endpoint_url": "https://your-api.com/process"
    }
    
    Output:
    {
        "job_id": "job_20251004_123456_abc123de",
        "brand": "telegram",
        "appstore": {...},
        "googleplay": {...},
        "trustpilot": {...},
        "reddit": {...},
        "news": {...},
        "limit": 50,
        "endpoint_url": "https://your-api.com/process",
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
        
        # Extract source configurations (all optional)
        appstore_config = event.get('appstore', {})
        googleplay_config = event.get('googleplay', {})
        trustpilot_config = event.get('trustpilot', {})
        reddit_config = event.get('reddit', {})
        news_config = event.get('news', {})
        
        # Add default values for optional fields to prevent JsonPath null errors
        if appstore_config and not isinstance(appstore_config, dict):
            appstore_config = {}
        if appstore_config:
            appstore_config.setdefault('country', 'us')
        
        if googleplay_config and not isinstance(googleplay_config, dict):
            googleplay_config = {}
        if googleplay_config:
            googleplay_config.setdefault('country', 'us')
        
        if reddit_config and not isinstance(reddit_config, dict):
            reddit_config = {}
        if reddit_config:
            reddit_config.setdefault('days_back', 30)
            reddit_config.setdefault('sort', 'new')
        
        if news_config and not isinstance(news_config, dict):
            news_config = {}
        if news_config:
            news_config.setdefault('search_type', 'everything')
            news_config.setdefault('language', 'en')
        
        # Check if at least one source is provided
        has_sources = any([
            appstore_config, 
            googleplay_config, 
            trustpilot_config, 
            reddit_config, 
            news_config
        ])
        
        if not has_sources:
            raise ValueError("At least one source must be configured (appstore, googleplay, trustpilot, reddit, or news)")
        
        # Global limit (can be overridden per source)
        global_limit = event.get('limit', 50)
        if not isinstance(global_limit, int) or global_limit < 1 or global_limit > 500:
            raise ValueError("Field 'limit' must be an integer between 1 and 500")
        
        # Processing endpoint URL (optional)
        processing_endpoint_url = event.get('processing_endpoint_url', 'https://webhook.site/test-endpoint')
        
        # Generate unique job_id
        timestamp = datetime.utcnow()
        job_id = f"job_{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Log configuration
        active_sources = []
        if appstore_config:
            active_sources.append('appstore')
        if googleplay_config:
            active_sources.append('googleplay')
        if trustpilot_config:
            active_sources.append('trustpilot')
        if reddit_config:
            active_sources.append('reddit')
        if news_config:
            active_sources.append('news')
        
        logger.info(f"✅ Generated job_id: {job_id}")
        logger.info(f"   Brand: {brand}")
        logger.info(f"   Active sources: {active_sources}")
        logger.info(f"   Global limit: {global_limit}")
        
        # Prepare output - pass through all configurations
        result = {
            'job_id': job_id,
            'brand': brand,
            'appstore': appstore_config,
            'googleplay': googleplay_config,
            'trustpilot': trustpilot_config,
            'reddit': reddit_config,
            'news': news_config,
            'limit': global_limit,
            'endpoint_url': processing_endpoint_url,
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

