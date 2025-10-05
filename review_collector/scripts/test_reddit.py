#!/usr/bin/env python3
"""
Test Reddit API Integration

Tests fetching posts mentioning a brand from Reddit using PRAW (Python Reddit API Wrapper).
This script searches for brand mentions in the last month across Reddit.

Setup:
1. Install PRAW: pip install praw
2. Create Reddit App at: https://www.reddit.com/prefs/apps
3. Set environment variables:
   - REDDIT_CLIENT_ID
   - REDDIT_CLIENT_SECRET
   - REDDIT_USER_AGENT (e.g., "Brand Monitor v1.0")

Usage:
    python test_reddit.py --brand "Tesla" --limit 50
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

try:
    import praw
    from praw.models import Submission
except ImportError:
    print("❌ PRAW not installed. Install it with: pip install praw")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RedditClient:
    """
    Client for Reddit API using PRAW.
    
    Searches for posts mentioning a specific brand across all subreddits.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit client.
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string (e.g., "Brand Monitor v1.0")
        """
        if not all([client_id, client_secret, user_agent]):
            raise ValueError("Reddit credentials are required")
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test authentication
        logger.info(f"✅ Connected to Reddit API")
        logger.info(f"   Read-only: {self.reddit.read_only}")
        logger.info(f"   User agent: {user_agent}")
    
    def search_brand_mentions(
        self,
        brand: str,
        limit: int = 100,
        days_back: int = 30,
        sort: str = "new"
    ) -> List[Dict[str, Any]]:
        """
        Search for posts mentioning a brand in the last N days.
        
        Args:
            brand: Brand name to search for
            limit: Maximum number of posts to fetch
            days_back: How many days back to search
            sort: Sort order - 'new', 'hot', 'relevance', 'top'
            
        Returns:
            List of post dictionaries
        """
        logger.info(f"🔍 Searching Reddit for: '{brand}'")
        logger.info(f"   Time range: Last {days_back} days")
        logger.info(f"   Limit: {limit} posts")
        logger.info(f"   Sort by: {sort}")
        
        # Calculate timestamp for filtering
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        cutoff_timestamp = cutoff_date.timestamp()
        
        posts = []
        try:
            # Search across all of Reddit
            search_query = f'"{brand}"'  # Use quotes for exact phrase
            
            logger.info(f"   Query: {search_query}")
            
            # Use subreddit 'all' to search across all subreddits
            subreddit = self.reddit.subreddit('all')
            
            # Search with specified sort order
            search_results = subreddit.search(
                search_query,
                sort=sort,
                time_filter='month',  # Reddit's built-in time filter
                limit=limit * 2  # Fetch extra because we'll filter by exact date
            )
            
            fetched_count = 0
            filtered_count = 0
            
            for submission in search_results:
                fetched_count += 1
                
                # Filter by exact date
                if submission.created_utc < cutoff_timestamp:
                    filtered_count += 1
                    continue
                
                post_data = self._extract_post_data(submission, brand)
                posts.append(post_data)
                
                # Stop if we've reached the limit
                if len(posts) >= limit:
                    break
            
            logger.info(f"✅ Found {len(posts)} posts (fetched: {fetched_count}, filtered out: {filtered_count})")
            
        except Exception as e:
            logger.error(f"❌ Error searching Reddit: {e}", exc_info=True)
            raise
        
        return posts
    
    def _extract_post_data(self, submission: Submission, brand: str) -> Dict[str, Any]:
        """
        Extract relevant data from Reddit submission.
        
        Args:
            submission: PRAW Submission object
            brand: Brand name (for storage)
            
        Returns:
            Dictionary with post data
        """
        # Calculate post age
        created_dt = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
        age_days = (datetime.now(timezone.utc) - created_dt).days
        
        return {
            'id': submission.id,
            'title': submission.title,
            'text': submission.selftext,  # Post body (empty for link posts)
            'author': str(submission.author) if submission.author else '[deleted]',
            'subreddit': str(submission.subreddit),
            'score': submission.score,  # Upvotes - downvotes
            'upvote_ratio': submission.upvote_ratio,  # Percentage of upvotes
            'num_comments': submission.num_comments,
            'created_utc': submission.created_utc,
            'created_date': created_dt.isoformat(),
            'url': submission.url,  # Link URL (for link posts)
            'permalink': f"https://www.reddit.com{submission.permalink}",
            'is_self': submission.is_self,  # True for text posts, False for links
            'over_18': submission.over_18,
            'spoiler': submission.spoiler,
            'stickied': submission.stickied,
            'locked': submission.locked,
            'brand': brand,
            'age_days': age_days,
            # Additional metadata
            'link_flair_text': submission.link_flair_text,
            'domain': submission.domain,  # Domain for link posts
        }


def format_post_summary(post: Dict[str, Any]) -> str:
    """Format a post for console display."""
    lines = [
        f"\n{'='*80}",
        f"📝 {post['title']}",
        f"{'='*80}",
        f"👤 Author: u/{post['author']}",
        f"📍 Subreddit: r/{post['subreddit']}",
        f"🔗 {post['permalink']}",
        f"📅 Posted: {post['created_date']} ({post['age_days']} days ago)",
        f"⬆️  Score: {post['score']} | Upvote ratio: {post['upvote_ratio']:.1%} | Comments: {post['num_comments']}",
        f"🏷️  Type: {'Text post' if post['is_self'] else f'Link to {post['domain']}'}"
    ]
    
    if post['link_flair_text']:
        lines.append(f"🏷️  Flair: {post['link_flair_text']}")
    
    # Show preview of text
    if post['text']:
        preview = post['text'][:200].replace('\n', ' ')
        if len(post['text']) > 200:
            preview += "..."
        lines.append(f"\n{preview}")
    elif not post['is_self']:
        lines.append(f"\n🔗 Link: {post['url']}")
    
    return '\n'.join(lines)


def save_results_to_json(posts: List[Dict[str, Any]], brand: str, output_dir: str = "."):
    """Save results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/reddit_{brand.lower().replace(' ', '_')}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Saved {len(posts)} posts to: {filename}")
    return filename


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test Reddit API for brand mentions')
    parser.add_argument('--brand', type=str, required=True, help='Brand name to search for')
    parser.add_argument('--limit', type=int, default=50, help='Maximum number of posts to fetch')
    parser.add_argument('--days', type=int, default=30, help='Days back to search')
    parser.add_argument('--sort', type=str, default='new', 
                       choices=['new', 'hot', 'relevance', 'top'],
                       help='Sort order')
    parser.add_argument('--save', action='store_true', help='Save results to JSON file')
    parser.add_argument('--quiet', action='store_true', help='Only show summary')
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("🧪 Reddit API Test Script")
    logger.info("=" * 80)
    
    # Get credentials from environment variables
    client_id = os.environ.get('REDDIT_CLIENT_ID')
    client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
    user_agent = os.environ.get('REDDIT_USER_AGENT', 'Brand Monitor v1.0')
    
    if not client_id or not client_secret:
        logger.error("❌ Missing credentials!")
        logger.error("   Set the following environment variables:")
        logger.error("   - REDDIT_CLIENT_ID")
        logger.error("   - REDDIT_CLIENT_SECRET")
        logger.error("   - REDDIT_USER_AGENT (optional)")
        logger.error("\n   Get credentials at: https://www.reddit.com/prefs/apps")
        sys.exit(1)
    
    try:
        # Initialize client
        client = RedditClient(client_id, client_secret, user_agent)
        
        # Search for brand mentions
        posts = client.search_brand_mentions(
            brand=args.brand,
            limit=args.limit,
            days_back=args.days,
            sort=args.sort
        )
        
        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESULTS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total posts found: {len(posts)}")
        
        if posts:
            # Statistics
            total_score = sum(p['score'] for p in posts)
            total_comments = sum(p['num_comments'] for p in posts)
            avg_upvote_ratio = sum(p['upvote_ratio'] for p in posts) / len(posts)
            
            subreddits = {}
            for post in posts:
                subreddit = post['subreddit']
                subreddits[subreddit] = subreddits.get(subreddit, 0) + 1
            
            logger.info(f"Total score (upvotes): {total_score}")
            logger.info(f"Total comments: {total_comments}")
            logger.info(f"Average upvote ratio: {avg_upvote_ratio:.1%}")
            logger.info(f"Unique subreddits: {len(subreddits)}")
            
            # Top subreddits
            top_subreddits = sorted(subreddits.items(), key=lambda x: x[1], reverse=True)[:5]
            logger.info("\n🏆 Top Subreddits:")
            for subreddit, count in top_subreddits:
                logger.info(f"   r/{subreddit}: {count} posts")
            
            # Show individual posts (unless quiet mode)
            if not args.quiet:
                logger.info("\n" + "=" * 80)
                logger.info("📝 POSTS")
                logger.info("=" * 80)
                
                for i, post in enumerate(posts[:10], 1):  # Show first 10
                    print(format_post_summary(post))
                
                if len(posts) > 10:
                    logger.info(f"\n... and {len(posts) - 10} more posts")
            
            # Save to JSON if requested
            if args.save:
                save_results_to_json(posts, args.brand)
        
        else:
            logger.warning(f"⚠️  No posts found for '{args.brand}' in the last {args.days} days")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Test completed successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

