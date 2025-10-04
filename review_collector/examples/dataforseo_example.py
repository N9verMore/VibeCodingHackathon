#!/usr/bin/env python3
"""
Simple example of using DataForSEO Trustpilot Client

This script demonstrates basic usage of the DataForSEOTrustpilotClient
to fetch reviews from any business on Trustpilot.

Requirements:
    - DataForSEO account credentials
    - Python 3.8+
    - Required packages: requests

Usage:
    export DATAFORSEO_LOGIN="your@email.com"
    export DATAFORSEO_PASSWORD="your_password"
    python dataforseo_example.py
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'serpapi_collector'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'shared'))

from dataforseo_trustpilot_client import DataForSEOTrustpilotClient


def main():
    # Get credentials from environment
    login = os.environ.get('DATAFORSEO_LOGIN', 'mglushko@perfsys.com')
    password = os.environ.get('DATAFORSEO_PASSWORD', 'cd0bdc42c24cad76')
    
    print("=" * 60)
    print("DataForSEO Trustpilot Client - Simple Example")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Initializing client...")
    client = DataForSEOTrustpilotClient(
        login=login,
        password=password
    )
    print("✅ Client initialized")
    
    # Example 1: Zara reviews
    print("\n2. Fetching reviews for Zara...")
    reviews = client.fetch_reviews(
        app_identifier="www.zara.com",
        brand="zara",
        limit=10  # Just 10 for quick demo
    )
    
    print(f"✅ Fetched {len(reviews)} reviews")
    
    # Display first review
    if reviews:
        print("\n3. Sample review:")
        print("-" * 60)
        review = reviews[0]
        print(f"Rating: {'⭐' * review.rating}")
        print(f"Title: {review.title}")
        print(f"Author: {review.author_hint}")
        print(f"Date: {review.created_at.strftime('%Y-%m-%d')}")
        if review.text:
            text = review.text[:200] + '...' if len(review.text) > 200 else review.text
            print(f"Text: {text}")
        print(f"Link: {review.backlink}")
    
    # Show statistics
    print("\n4. Statistics:")
    print("-" * 60)
    rating_counts = {}
    for review in reviews:
        rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
    
    for rating in range(5, 0, -1):
        count = rating_counts.get(rating, 0)
        print(f"{'⭐' * rating} ({rating}): {count} reviews")
    
    avg = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    print(f"\nAverage rating: {avg:.2f}⭐")
    
    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

