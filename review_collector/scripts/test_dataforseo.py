#!/usr/bin/env python3
"""
Test script for DataForSEO Trustpilot API

Usage:
    python test_dataforseo.py --domain www.zara.com --limit 40
    
Environment Variables:
    DATAFORSEO_LOGIN: DataForSEO login email
    DATAFORSEO_PASSWORD: DataForSEO password
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'serpapi_collector'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'shared'))

from dataforseo_trustpilot_client import DataForSEOTrustpilotClient


def main():
    parser = argparse.ArgumentParser(description='Test DataForSEO Trustpilot API')
    parser.add_argument('--domain', required=True, help='Trustpilot domain (e.g., www.zara.com)')
    parser.add_argument('--brand', default='test', help='Brand name for tracking')
    parser.add_argument('--limit', type=int, default=40, help='Number of reviews to fetch')
    parser.add_argument('--login', help='DataForSEO login (or set DATAFORSEO_LOGIN env var)')
    parser.add_argument('--password', help='DataForSEO password (or set DATAFORSEO_PASSWORD env var)')
    parser.add_argument('--output', help='Output JSON file path (optional)')
    
    args = parser.parse_args()
    
    # Get credentials
    login = args.login or os.environ.get('DATAFORSEO_LOGIN')
    password = args.password or os.environ.get('DATAFORSEO_PASSWORD')
    
    if not login or not password:
        print("❌ Error: DataForSEO credentials required")
        print("   Set --login and --password or DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD env vars")
        sys.exit(1)
    
    print("=" * 60)
    print("🧪 DataForSEO Trustpilot API Test")
    print("=" * 60)
    print(f"Domain: {args.domain}")
    print(f"Brand: {args.brand}")
    print(f"Limit: {args.limit}")
    print(f"Login: {login}")
    print("=" * 60)
    
    try:
        # Initialize client
        print("\n🔧 Initializing DataForSEO client...")
        client = DataForSEOTrustpilotClient(
            login=login,
            password=password,
            timeout=30,
            max_poll_attempts=20,
            poll_interval=3
        )
        print("✅ Client initialized")
        
        # Fetch reviews
        print(f"\n🚀 Fetching reviews for {args.domain}...")
        reviews = client.fetch_reviews(
            app_identifier=args.domain,
            brand=args.brand,
            limit=args.limit
        )
        
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS! Retrieved {len(reviews)} reviews")
        print("=" * 60)
        
        # Display sample reviews
        print("\n📝 Sample Reviews:")
        print("-" * 60)
        
        for i, review in enumerate(reviews[:5], 1):
            print(f"\n{i}. Rating: {'⭐' * review.rating}")
            print(f"   Title: {review.title}")
            print(f"   Author: {review.author_hint}")
            print(f"   Date: {review.created_at.strftime('%Y-%m-%d')}")
            if review.text:
                text_preview = review.text[:100] + '...' if len(review.text) > 100 else review.text
                print(f"   Text: {text_preview}")
        
        if len(reviews) > 5:
            print(f"\n   ... and {len(reviews) - 5} more reviews")
        
        # Statistics
        print("\n" + "=" * 60)
        print("📊 Statistics:")
        print("-" * 60)
        
        rating_counts = {i: 0 for i in range(1, 6)}
        for review in reviews:
            rating_counts[review.rating] += 1
        
        print(f"Total reviews: {len(reviews)}")
        print("\nRating distribution:")
        for rating in range(5, 0, -1):
            count = rating_counts[rating]
            percentage = (count / len(reviews) * 100) if reviews else 0
            bar = '█' * int(percentage / 2)
            print(f"  {'⭐' * rating} ({rating}): {count:3d} [{percentage:5.1f}%] {bar}")
        
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
        print(f"\nAverage rating: {avg_rating:.2f} ⭐")
        
        # Save to file if requested
        if args.output:
            print(f"\n💾 Saving results to {args.output}...")
            output_data = {
                'metadata': {
                    'domain': args.domain,
                    'brand': args.brand,
                    'limit': args.limit,
                    'fetched_at': datetime.utcnow().isoformat(),
                    'total_reviews': len(reviews)
                },
                'reviews': [
                    {
                        'id': r.id,
                        'title': r.title,
                        'text': r.text,
                        'rating': r.rating,
                        'author': r.author_hint,
                        'created_at': r.created_at.isoformat(),
                        'backlink': r.backlink
                    }
                    for r in reviews
                ]
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results saved to {args.output}")
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

