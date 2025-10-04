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
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'AWS-Lambda-HTTP-Caller/1.0'
            },
            timeout=25.0  # Leave 5 seconds for Lambda overhead
        )
        
        status_code = response.status
        logger.info(f"📥 Response status: {status_code}")
        
        # Parse response
        response_data = None
        if response.data:
            try:
                response_data = json.loads(response.data.decode('utf-8'))
                logger.info(f"   Response data: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                response_text = response.data.decode('utf-8')
                logger.warning(f"   Response is not JSON: {response_text[:200]}")
                response_data = {'raw_response': response_text}
        
        # Check if successful
        success = 200 <= status_code < 300
        
        result = {
            'success': success,
            'status_code': status_code,
            'response': response_data,
            'endpoint_url': endpoint_url
        }
        
        if success:
            logger.info("✅ HTTP call completed successfully")
        else:
            logger.warning(f"⚠️ HTTP call returned non-success status: {status_code}")
        
        return result
        
    except urllib3.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP error: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'HTTPError',
            'message': str(e)
        }
    except Exception as e:
        logger.error(f"❌ HTTP call failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': type(e).__name__,
            'message': str(e)
        }

