# ============================================
# FILE: app/services/processing_service.py
# ============================================
import logging
import asyncio
from typing import Dict, List, Tuple
from app.models import ProcessedReview, ReviewFromDB
from app.services.dynamodb_service import DynamoDBService
from app.services.openai_service import OpenAIService
from app.services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)


class ReviewProcessingService:
    """Головний сервіс обробки відгуків"""

    def __init__(
            self,
            db_service: DynamoDBService,
            openai_service: OpenAIService,
            delivery_service: DeliveryService,
            batch_size: int = 10
    ):
        self.db_service = db_service
        self.openai_service = openai_service
        self.delivery_service = delivery_service
        self.batch_size = batch_size
        logger.info(f"ReviewProcessingService initialized with batch_size={batch_size}")

    async def process_reviews(self) -> Dict:
        """
        Основний метод обробки відгуків з batch аналізом та паралелізмом

        Returns:
            Dict: Статистика обробки
        """
        # 1. Отримуємо необроблені відгуки
        logger.info("Fetching unprocessed reviews from DynamoDB...")
        unprocessed_reviews = await self.db_service.get_unprocessed_reviews()

        if not unprocessed_reviews:
            logger.info("No unprocessed reviews found")
            return {"processed": 0, "message": "No reviews to process"}

        logger.info(f"Found {len(unprocessed_reviews)} unprocessed reviews")

        # 2. Розбиваємо на батчі по batch_size
        batches = self._split_into_batches(unprocessed_reviews, self.batch_size)
        logger.info(f"Split into {len(batches)} batches of {self.batch_size} reviews each")

        # 3. Обробляємо всі батчі ПАРАЛЕЛЬНО
        logger.info("Starting parallel batch processing...")
        tasks = [self._process_batch(batch) for batch in batches]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 4. Збираємо статистику
        total_analyzed = 0
        total_delivered = 0
        total_marked = 0
        failed_batches = 0

        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed: {str(result)}")
                failed_batches += 1
            elif result:
                total_analyzed += result.get('analyzed', 0)
                total_delivered += result.get('delivered', 0)
                total_marked += result.get('marked', 0)

        logger.info(f"Processing complete: {total_analyzed} analyzed, {total_delivered} delivered")

        return {
            "analyzed": total_analyzed,
            "delivered": total_delivered,
            "marked_as_processed": total_marked,
            "failed_batches": failed_batches,
            "total": len(unprocessed_reviews),
            "batch_size": self.batch_size,
            "batches_processed": len(batches),
            "message": f"Analyzed {total_analyzed}, delivered {total_delivered}, marked {total_marked} out of {len(unprocessed_reviews)} reviews"
        }

    async def _process_batch(self, reviews_batch: List[ReviewFromDB]) -> Dict:
        """
        Обробляє один батч відгуків (всі в одному промпті OpenAI)

        Args:
            reviews_batch: Батч відгуків для обробки

        Returns:
            Dict: Статистика обробки батчу
        """
        batch_id = f"{reviews_batch[0].id[:8]}...{reviews_batch[-1].id[:8]}"
        logger.info(f"[Batch {batch_id}] Processing {len(reviews_batch)} items...")

        try:
            # Розділяємо на новини та відгуки
            news_items = [r for r in reviews_batch if r.source.value == "news"]
            review_items = [r for r in reviews_batch if r.source.value != "news"]
            
            processed_reviews = []
            batch_ids = []
            
            # 1. Обробляємо звичайні відгуки батчем
            if review_items:
                logger.info(f"[Batch {batch_id}] Analyzing {len(review_items)} reviews in batch...")
                analyses = await self.openai_service.analyze_reviews_batch(review_items)
                
                for review, analysis in zip(review_items, analyses):
                    processed_reviews.append(ProcessedReview(
                        id=review.id,
                        source=review.source,
                        backlink=review.backlink,
                        text=review.text,
                        rating=review.rating,
                        created_at=review.created_at,
                        sentiment=analysis.sentiment,
                        description=analysis.description,
                        categories=analysis.categories,
                        severity=analysis.severity,
                        is_processed=True
                    ))
                    batch_ids.append((review.source.value, review.id))
            
            # 2. Обробляємо новини окремо (з web search)
            if news_items:
                logger.info(f"[Batch {batch_id}] Analyzing {len(news_items)} news items individually...")
                for news_item in news_items:
                    try:
                        analysis = await self.openai_service.analyze_news(news_item.backlink)
                        processed_reviews.append(ProcessedReview(
                            id=news_item.id,
                            source=news_item.source,
                            backlink=news_item.backlink,
                            text=news_item.text,
                            rating=None,  # News не мають rating
                            created_at=news_item.created_at,
                            sentiment=analysis.sentiment,
                            description=analysis.description,
                            categories=analysis.categories,
                            severity=analysis.severity,
                            is_processed=True
                        ))
                        batch_ids.append((news_item.source.value, news_item.id))
                    except Exception as e:
                        logger.error(f"[Batch {batch_id}] Failed to analyze news {news_item.id}: {str(e)}")
                        continue

            logger.info(f"[Batch {batch_id}] All {len(processed_reviews)} items analyzed successfully")

            # 3. Доставляємо батч (атомарна операція)
            delivery_success = await self._deliver_batch(processed_reviews, batch_ids, batch_id)

            if delivery_success:
                logger.info(f"[Batch {batch_id}] ✅ Complete: analyzed, delivered, and marked")
                return {
                    'analyzed': len(processed_reviews),
                    'delivered': len(processed_reviews),
                    'marked': len(processed_reviews)
                }
            else:
                logger.warning(f"[Batch {batch_id}] ❌ Analysis done but delivery failed")
                return {
                    'analyzed': len(processed_reviews),
                    'delivered': 0,
                    'marked': 0
                }

        except Exception as e:
            logger.error(f"[Batch {batch_id}] Failed to process: {str(e)}")
            return {
                'analyzed': 0,
                'delivered': 0,
                'marked': 0
            }

    async def _deliver_batch(
        self, 
        batch: List[ProcessedReview], 
        batch_ids: List[Tuple[str, str]],
        batch_id: str
    ) -> bool:
        """
        Доставляє батч відгуків, маркує як оброблені та зберігає в Postgres

        Args:
            batch: Список оброблених відгуків
            batch_ids: Список (source, id) для маркування
            batch_id: ID батчу для логування

        Returns:
            bool: True якщо доставка і маркування успішні
        """
        try:
            # Спроба доставити
            logger.info(f"[Batch {batch_id}] Delivering {len(batch)} reviews...")
            await self.delivery_service.deliver_processed_reviews(batch)
            
            # Якщо доставка успішна - маркуємо як оброблені
            logger.info(f"[Batch {batch_id}] Delivery successful, marking as processed...")
            
            for source, review_id in batch_ids:
                await self.db_service.mark_as_processed(source, review_id)
            
            logger.info(f"[Batch {batch_id}] Successfully marked {len(batch_ids)} reviews as processed")
            
            return True
            
        except Exception as e:
            logger.error(f"[Batch {batch_id}] Delivery failed: {str(e)}")
            logger.error(f"[Batch {batch_id}] Reviews will remain unprocessed for retry")
            return False

    def _split_into_batches(self, items: List, batch_size: int) -> List[List]:
        """
        Розбиває список на батчі

        Args:
            items: Список елементів
            batch_size: Розмір батчу

        Returns:
            List[List]: Список батчів
        """
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches
