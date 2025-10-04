#!/usr/bin/env python3
"""
Manual Review Collection Trigger (Python)

Provides programmatic way to trigger review collection via AWS Lambda.
Can be used standalone or imported as a module.
"""

import json
import boto3
import argparse
from typing import Dict, Any, Optional


class ReviewCollector:
    """Client for triggering review collection"""
    
    def __init__(self, function_name: str = "serpapi-collector-lambda", region: str = "us-east-1"):
        """
        Initialize collector client.
        
        Args:
            function_name: Lambda function name
            region: AWS region
        """
        self.function_name = function_name
        self.lambda_client = boto3.client('lambda', region_name=region)
    
    def collect(
        self,
        source: str,
        app_identifier: str,
        brand: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Trigger review collection.
        
        Args:
            source: Review source (appstore, googleplay, trustpilot)
            app_identifier: App/product identifier
            brand: Brand name
            limit: Maximum number of reviews
            
        Returns:
            Response dictionary with statistics
        """
        payload = {
            'source': source,
            'app_identifier': app_identifier,
            'brand': brand,
            'limit': limit
        }
        
        print(f"🚀 Triggering collection for {brand} ({source})...")
        print(f"   App ID: {app_identifier}")
        print(f"   Limit: {limit}")
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',  # Synchronous
                Payload=json.dumps(payload)
            )
            
            # Parse response
            response_payload = json.loads(response['Payload'].read())
            
            # Extract body
            if 'body' in response_payload:
                body = json.loads(response_payload['body']) if isinstance(response_payload['body'], str) else response_payload['body']
            else:
                body = response_payload
            
            # Check status
            status_code = response_payload.get('statusCode', 200)
            
            if status_code == 200:
                stats = body.get('statistics', {})
                print(f"\n✅ Success!")
                print(f"   Fetched: {stats.get('fetched', 0)}")
                print(f"   Saved: {stats.get('saved', 0)}")
                print(f"   Skipped: {stats.get('skipped', 0)}")
                print(f"   Duration: {stats.get('duration_seconds', 0):.2f}s")
            else:
                print(f"\n❌ Error: {body.get('message', 'Unknown error')}")
            
            return body
            
        except Exception as e:
            print(f"\n❌ Failed to invoke Lambda: {e}")
            raise


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Manually trigger review collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect Telegram reviews from App Store
  %(prog)s --source appstore --app-id 544007664 --brand telegram --limit 50
  
  # Collect WhatsApp reviews from Google Play
  %(prog)s --source googleplay --app-id com.whatsapp --brand whatsapp
  
  # Collect Trustpilot reviews
  %(prog)s --source trustpilot --app-id tesla.com --brand tesla --limit 20
        """
    )
    
    parser.add_argument(
        '--source',
        required=True,
        choices=['appstore', 'googleplay', 'trustpilot'],
        help='Review source platform'
    )
    
    parser.add_argument(
        '--app-id',
        required=True,
        help='App/product identifier'
    )
    
    parser.add_argument(
        '--brand',
        required=True,
        help='Brand name'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum number of reviews (default: 100)'
    )
    
    parser.add_argument(
        '--function-name',
        default='serpapi-collector-lambda',
        help='Lambda function name (default: serpapi-collector-lambda)'
    )
    
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    
    args = parser.parse_args()
    
    # Create collector and trigger
    collector = ReviewCollector(
        function_name=args.function_name,
        region=args.region
    )
    
    collector.collect(
        source=args.source,
        app_identifier=args.app_id,
        brand=args.brand,
        limit=args.limit
    )


if __name__ == '__main__':
    main()

