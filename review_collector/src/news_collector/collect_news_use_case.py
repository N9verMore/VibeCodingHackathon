"""
Collect News Use Case - Business Logic

Orchestrates the process of fetching news articles from NewsAPI
and storing them in the database.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date

from newsapi_client import NewsAPIClient
from news_repository import NewsArticleRepository
from news_article import NewsArticle


logger = logging.getLogger(__name__)


class CollectNewsUseCase:
    """
    Use case for collecting news articles.
    
    Responsibilities:
    - Fetch articles from NewsAPI
    - Convert to NewsArticle entities
    - Store in database with idempotency
    - Return statistics
    """
    
    def __init__(self, client: NewsAPIClient, repository: NewsArticleRepository):
        """
        Initialize use case.
        
        Args:
            client: NewsAPI client
            repository: NewsArticle repository
        """
        self.client = client
        self.repository = repository
    
    def execute(
        self,
        brand: str,
        limit: int = 100,
        search_type: str = "everything",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        language: Optional[str] = None,
        country: Optional[str] = None,
        category: Optional[str] = None,
        sources: Optional[str] = None,
        search_in: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute news collection workflow.
        
        Args:
            brand: Search query/keyword (e.g., 'Tesla', 'Apple')
            limit: Maximum number of articles to collect
            search_type: 'everything' or 'top-headlines'
            from_date: Start date for articles (everything only)
            to_date: End date for articles (everything only)
            language: Language code (everything only)
            country: Country code (top-headlines only)
            category: News category (top-headlines only)
            sources: Comma-separated source IDs (top-headlines only)
            search_in: Where to search - 'title', 'description', or 'content' (everything only)
            
        Returns:
            Statistics dictionary with collection results
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info(f"🎯 Starting news collection for brand: {brand}")
        logger.info(f"   Search type: {search_type}")
        logger.info(f"   Limit: {limit}")
        logger.info("=" * 60)
        
        try:
            # Step 1: Fetch articles from NewsAPI
            kwargs = {}
            
            if search_type == "everything":
                if from_date:
                    kwargs['from_date'] = from_date
                if to_date:
                    kwargs['to_date'] = to_date
                if language:
                    kwargs['language'] = language
                if search_in:
                    kwargs['search_in'] = search_in
            elif search_type == "top-headlines":
                if country:
                    kwargs['country'] = country
                if category:
                    kwargs['category'] = category
                if sources:
                    kwargs['sources'] = sources
            
            logger.info("📡 Fetching articles from NewsAPI...")
            raw_articles = self.client.fetch_articles(
                query=brand,
                limit=limit,
                search_type=search_type,
                **kwargs
            )
            
            logger.info(f"✅ Fetched {len(raw_articles)} articles")
            
            if not raw_articles:
                logger.warning("No articles found")
                return self._create_stats(
                    brand=brand,
                    fetched=0,
                    saved=0,
                    skipped=0,
                    errors=0,
                    start_time=start_time
                )
            
            # Step 2: Convert to NewsArticle entities
            logger.info("🔄 Converting to NewsArticle entities...")
            articles = self._convert_to_entities(raw_articles, brand, country)
            logger.info(f"✅ Converted {len(articles)} articles")
            
            # Step 3: Save to database
            logger.info("💾 Saving articles to database...")
            save_stats = self.repository.batch_save(articles)
            logger.info(f"✅ Save complete: {save_stats}")
            
            # Step 4: Return statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            stats = {
                'brand': brand,
                'search_type': search_type,
                'fetched': len(raw_articles),
                'saved': save_stats['written'],
                'skipped': save_stats['skipped'],
                'errors': save_stats['errors'],
                'duration_seconds': round(duration, 2),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
            logger.info("=" * 60)
            logger.info("✅ News collection completed successfully")
            logger.info(f"   Statistics: {stats}")
            logger.info("=" * 60)
            
            return stats
        
        except Exception as e:
            logger.error(f"❌ News collection failed: {e}", exc_info=True)
            raise
    
    def _convert_to_entities(
        self,
        raw_articles: List[Dict[str, Any]],
        brand: str,
        country: Optional[str]
    ) -> List[NewsArticle]:
        """
        Convert raw NewsAPI articles to NewsArticle entities.
        
        Args:
            raw_articles: List of raw article dicts from NewsAPI
            brand: Search term/brand
            country: Country code (optional)
            
        Returns:
            List of NewsArticle entities
        """
        articles = []
        
        for idx, raw_article in enumerate(raw_articles):
            try:
                article = self._map_article(raw_article, brand, country)
                articles.append(article)
            except Exception as e:
                logger.error(f"Failed to convert article {idx}: {e}")
                # Continue with other articles
        
        return articles
    
    def _map_article(
        self,
        raw: Dict[str, Any],
        brand: str,
        country: Optional[str]
    ) -> NewsArticle:
        """
        Map raw NewsAPI article to NewsArticle entity.
        
        Args:
            raw: Raw article dict from NewsAPI
            brand: Search term/brand
            country: Country code
            
        Returns:
            NewsArticle entity
        """
        # Extract source info
        source = raw.get("source", {})
        source_id = source.get("id") or "unknown"
        source_name = source.get("name", "Unknown")
        
        # Generate unique ID
        published_at_str = raw.get("publishedAt", "")
        title_snippet = raw.get("title", "")[:30].replace(" ", "-").replace("/", "-")
        article_id = f"{source_id}-{published_at_str[:10]}-{title_snippet}".lower()
        
        # Remove any problematic characters
        article_id = "".join(c for c in article_id if c.isalnum() or c in "-_")
        
        # Parse published date
        try:
            published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid publishedAt: {published_at_str}, using current time")
            published_at = datetime.utcnow()
        
        return NewsArticle(
            id=article_id,
            source_id=source_id,
            source_name=source_name,
            url=raw.get("url", ""),
            brand=brand.lower(),  # Зберігаємо в lowercase
            title=raw.get("title", "Untitled"),
            description=raw.get("description"),
            content=raw.get("content"),
            author=raw.get("author"),
            image_url=raw.get("urlToImage"),
            language=self._detect_language(raw),
            country=country,
            published_at=published_at,
            fetched_at=datetime.utcnow(),
            is_processed=False
        )
    
    def _detect_language(self, raw: Dict[str, Any]) -> str:
        """
        Detect or infer language from article.
        
        For now, defaults to 'en'. Can be enhanced with language detection library.
        """
        # TODO: Implement proper language detection if needed
        return "en"
    
    def _create_stats(
        self,
        brand: str,
        fetched: int,
        saved: int,
        skipped: int,
        errors: int,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Create statistics dictionary"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'brand': brand,
            'fetched': fetched,
            'saved': saved,
            'skipped': skipped,
            'errors': errors,
            'duration_seconds': round(duration, 2),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }

