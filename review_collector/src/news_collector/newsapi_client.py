"""
NewsAPI Client

Integration with NewsAPI.org for fetching news articles.
Documentation: https://newsapi.org/docs
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging


logger = logging.getLogger(__name__)


class NewsAPIClient:
    """
    Client for NewsAPI.org
    
    Supports both endpoints:
    - /everything: Search through millions of articles
    - /top-headlines: Get breaking news headlines
    """
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: str):
        """
        Initialize NewsAPI client.
        
        Args:
            api_key: NewsAPI API key (get from https://newsapi.org)
        """
        if not api_key:
            raise ValueError("NewsAPI key is required")
        
        self.api_key = api_key
        self.session = requests.Session()
        logger.info("Initialized NewsAPI client")
    
    def search_everything(
        self,
        query: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        language: Optional[str] = None,
        sort_by: str = "publishedAt",
        page_size: int = 100,
        page: int = 1,
        search_in: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search articles using /everything endpoint.
        
        Args:
            query: Keywords or phrases to search for (e.g., "Tesla", "Apple iPhone")
            from_date: Start date for articles (format: YYYY-MM-DD)
            to_date: End date for articles
            language: Language code (en, uk, etc.)
            sort_by: Sort order - 'relevancy', 'popularity', or 'publishedAt'
            page_size: Results per page (max 100)
            page: Page number
            search_in: Where to search - 'title', 'description', or 'content'
            
        Returns:
            Dict with 'status', 'totalResults', and 'articles' keys
            
        Raises:
            ValueError: If API returns error
            requests.HTTPError: If HTTP request fails
        """
        endpoint = f"{self.BASE_URL}/everything"
        
        params = {
            "q": query,
            "apiKey": self.api_key,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page
        }
        
        if from_date:
            params["from"] = from_date.isoformat()
        if to_date:
            params["to"] = to_date.isoformat()
        if language:
            params["language"] = language
        if search_in:
            params["searchIn"] = search_in
        
        logger.info(f"NewsAPI /everything request: query='{query}', page={page}")
        
        response = self.session.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown error")
            raise ValueError(f"NewsAPI error: {error_msg}")
        
        total = data.get("totalResults", 0)
        count = len(data.get("articles", []))
        logger.info(f"NewsAPI returned {count} articles (total available: {total})")
        
        return data
    
    def get_top_headlines(
        self,
        country: Optional[str] = None,
        category: Optional[str] = None,
        sources: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 100,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Get top headlines using /top-headlines endpoint.
        
        Args:
            country: 2-letter country code (us, gb, ua)
            category: Category (business, entertainment, health, science, sports, technology)
            sources: Comma-separated source IDs (e.g., "bbc-news,cnn")
            query: Keywords to search for in headlines
            page_size: Results per page (max 100)
            page: Page number
            
        Note: Cannot mix country/category with sources parameter
        
        Returns:
            Dict with 'status', 'totalResults', and 'articles' keys
            
        Raises:
            ValueError: If API returns error or invalid parameter combination
            requests.HTTPError: If HTTP request fails
        """
        if sources and (country or category):
            raise ValueError("Cannot use 'sources' with 'country' or 'category'")
        
        endpoint = f"{self.BASE_URL}/top-headlines"
        
        params = {
            "apiKey": self.api_key,
            "pageSize": page_size,
            "page": page
        }
        
        if country:
            params["country"] = country
        if category:
            params["category"] = category
        if sources:
            params["sources"] = sources
        if query:
            params["q"] = query
        
        logger.info(f"NewsAPI /top-headlines request: country={country}, category={category}")
        
        response = self.session.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown error")
            raise ValueError(f"NewsAPI error: {error_msg}")
        
        count = len(data.get("articles", []))
        logger.info(f"NewsAPI returned {count} top headlines")
        
        return data
    
    def fetch_articles(
        self,
        query: str,
        limit: int = 100,
        search_type: str = "everything",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Unified method to fetch articles with automatic pagination.
        
        Args:
            query: Search query or keyword
            limit: Maximum number of articles to fetch
            search_type: "everything" or "top-headlines"
            **kwargs: Additional parameters for specific endpoints
                - from_date, to_date, language, sort_by (for everything)
                - country, category, sources (for top-headlines)
        
        Returns:
            List of article dictionaries
        """
        articles = []
        page = 1
        page_size = min(100, limit)  # NewsAPI max page size is 100
        
        while len(articles) < limit:
            try:
                if search_type == "everything":
                    data = self.search_everything(
                        query=query,
                        page_size=page_size,
                        page=page,
                        **kwargs
                    )
                elif search_type == "top-headlines":
                    data = self.get_top_headlines(
                        query=query,
                        page_size=page_size,
                        page=page,
                        **kwargs
                    )
                else:
                    raise ValueError(f"Invalid search_type: {search_type}")
                
                batch = data.get("articles", [])
                if not batch:
                    logger.info("No more articles available")
                    break
                
                articles.extend(batch)
                
                # Check if we've fetched everything available
                total_results = data.get("totalResults", 0)
                if len(articles) >= total_results:
                    logger.info(f"Fetched all {total_results} available articles")
                    break
                
                # Check if we've reached the limit
                if len(articles) >= limit:
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        result = articles[:limit]
        logger.info(f"Fetched total of {len(result)} articles")
        return result

