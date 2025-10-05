"""
HTTP Caller Lambda Handler

Calls external processing endpoint with collected data.
"""

import json
import logging
import urllib3
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize HTTP client
http = urllib3.PoolManager()


def lambda_handler(event, context):
    """
    Call external HTTP endpoint with collection results.
    
    Input:
    {
        "endpoint_url": "https://your-api.com/process",
        "job_id": "job_20251004_123456_abc123de",
        "brand": "telegram",
        "collection_results": [...]
    }
    
    Output:
    {
        "success": true,
        "status_code": 200,
        "response": {...}
    }
    """
    logger.info("=" * 60)
    logger.info("🌐 HTTP Caller Started")
    logger.info("=" * 60)
    logger.info(f"Event: {json.dumps(event, default=str, indent=2)}")
    
    try:
        # Extract parameters
        endpoint_url = event.get('endpoint_url')
        if not endpoint_url:
            raise ValueError("Field 'endpoint_url' is required")
        
        job_id = event.get('job_id')
        brand = event.get('brand')
        collection_results = event.get('collection_results', [])
        
        # Prepare payload
        payload = {
            'job_id': job_id,
            'brand': brand,
            'collection_results': collection_results
        }
        
        logger.info(f"📤 Calling endpoint: {endpoint_url}")
        logger.info(f"   Job ID: {job_id}")
        logger.info(f"   Brand: {brand}")
        logger.info(f"   Collection results count: {len(collection_results)}")
        
        # Make HTTP POST request
        encoded_data = json.dumps(payload).encode('utf-8')
        
        response = http.request(
            'POST',
            endpoint_url,
            body=encoded_data,
            headers={'Content-Type': 'application/json'},
            timeout=25.0  # 25 seconds timeout
        )
        
        logger.info(f"✅ HTTP call completed")
        logger.info(f"   Status Code: {response.status}")
        logger.info(f"   Response: {response.data.decode('utf-8')[:500]}")
        
        # Parse response
        response_data = {}
        if response.data:
            try:
                response_data = json.loads(response.data.decode('utf-8'))
            except json.JSONDecodeError:
                response_data = {'raw': response.data.decode('utf-8')}
        
        return {
            'success': True,
            'status_code': response.status,
            'response': response_data,
            'endpoint': endpoint_url
        }
        
    except Exception as e:
        logger.error(f"❌ HTTP call failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'endpoint': event.get('endpoint_url', 'unknown')
        }

