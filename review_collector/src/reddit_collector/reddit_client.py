"""
Reddit API Client

Integration with Reddit API using PRAW for fetching posts with brand mentions.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone

try:
    import praw
    from praw.models import Submission
except ImportError:
    # Will be installed in Lambda layer
    praw = None
    Submission = None


logger = logging.getLogger(__name__)


class RedditClient:
    """
    Client for Reddit API using PRAW.
    
    Searches for posts mentioning specific keywords across all subreddits.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit client.
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string
        """
        if not all([client_id, client_secret, user_agent]):
            raise ValueError("Reddit credentials are required")
        
        if praw is None:
            raise ImportError("PRAW library not installed")
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            read_only=True
        )
        
        logger.info(f"✅ Connected to Reddit API (read-only: {self.reddit.read_only})")
    
    def search_posts(
        self,
        keywords: str,
        limit: int = 100,
        days_back: int = 30,
        sort: str = "new"
    ) -> List[Dict[str, Any]]:
        """
        Search for posts containing specific keywords.
        
        Args:
            keywords: Keywords to search for (e.g., "Flo app")
            limit: Maximum number of posts to fetch
            days_back: How many days back to search
            sort: Sort order - 'new', 'hot', 'relevance', 'top'
            
        Returns:
            List of post dictionaries
        """
        logger.info(f"🔍 Searching Reddit for: '{keywords}'")
        logger.info(f"   Time range: Last {days_back} days")
        logger.info(f"   Limit: {limit} posts")
        logger.info(f"   Sort by: {sort}")
        
        # Calculate timestamp for filtering
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        cutoff_timestamp = cutoff_date.timestamp()
        
        posts = []
        try:
            # Search across all of Reddit
            search_query = f'"{keywords}"'  # Use quotes for exact phrase
            
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
                
                post_data = self._extract_post_data(submission, keywords)
                posts.append(post_data)
                
                # Stop if we've reached the limit
                if len(posts) >= limit:
                    break
            
            logger.info(f"✅ Found {len(posts)} posts (fetched: {fetched_count}, filtered out: {filtered_count})")
            
        except Exception as e:
            logger.error(f"❌ Error searching Reddit: {e}", exc_info=True)
            raise
        
        return posts
    
    def _extract_post_data(self, submission: Submission, keywords: str) -> Dict[str, Any]:
        """
        Extract relevant data from Reddit submission.
        
        Args:
            submission: PRAW Submission object
            keywords: Search keywords (for reference)
            
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
            'keywords': keywords,  # Store what was searched
            'age_days': age_days,
            # Additional metadata
            'link_flair_text': submission.link_flair_text,
            'domain': submission.domain,  # Domain for link posts
        }

