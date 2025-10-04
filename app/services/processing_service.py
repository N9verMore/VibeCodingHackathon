# ============================================
# FILE: app/services/processing_service.py
# ============================================
import logging
from typing import Dict, List, Tuple
from app.models import ProcessedReview
from .dynamodb_service import DynamoDBService
from .openai_service import OpenAIService
from .delivery_service import DeliveryService

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
        Основний метод обробки відгуків з батч-доставкою

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

        # 2. Обробляємо кожен відгук через OpenAI + батч-доставка
        current_batch = []  # ProcessedReview objects
        current_batch_ids = []  # (source, id) tuples для mark_as_processed
        
        total_analyzed = 0  # Скільки відгуків проаналізовано через LLM
        total_delivered = 0  # Скільки відгуків успішно доставлено
        total_marked = 0  # Скільки відгуків помічено як is_processed=True
        failed_analysis = 0  # Скільки відгуків не вдалося проаналізувати
        failed_delivery = 0  # Скільки батчів не вдалося доставити

        for idx, review in enumerate(unprocessed_reviews, start=1):
            try:
                logger.info(f"Processing review {review.id} ({idx}/{len(unprocessed_reviews)})...")

                # Аналіз через LLM
                analysis = await self.openai_service.analyze_review(review)

                # Створюємо оброблений відгук
                processed_review = ProcessedReview(
                    id=review.id,
                    source=review.source,
                    backlink=review.backlink,
                    text=review.text,
                    rating=review.rating,
                    created_at=review.created_at,
                    sentiment=analysis.sentiment,
                    description=analysis.description,
                    category=analysis.category,
                    is_processed=True
                )

                current_batch.append(processed_review)
                current_batch_ids.append((review.source.value, review.id))
                total_analyzed += 1
                
                logger.info(f"Review {review.id} analyzed successfully")

                # Перевіряємо чи заповнився батч
                if len(current_batch) >= self.batch_size:
                    logger.info(f"Batch of {len(current_batch)} reviews ready, delivering...")
                    
                    # Спроба доставити батч
                    delivery_success = await self._deliver_batch(current_batch, current_batch_ids)
                    
                    if delivery_success:
                        total_delivered += len(current_batch)
                        total_marked += len(current_batch)
                        logger.info(f"Batch delivered and marked successfully ({total_delivered}/{total_analyzed} delivered so far)")
                    else:
                        failed_delivery += 1
                        logger.warning(f"Batch delivery failed - reviews will NOT be marked as processed")
                    
                    # Очищаємо батч незалежно від результату
                    current_batch = []
                    current_batch_ids = []

            except Exception as e:
                logger.error(f"Failed to analyze review {review.id}: {str(e)}")
                failed_analysis += 1
                continue

        # 3. Відправляємо залишок (якщо є неповний батч)
        if current_batch:
            logger.info(f"Delivering final batch of {len(current_batch)} reviews...")
            
            delivery_success = await self._deliver_batch(current_batch, current_batch_ids)
            
            if delivery_success:
                total_delivered += len(current_batch)
                total_marked += len(current_batch)
                logger.info(f"Final batch delivered and marked ({total_delivered} total delivered)")
            else:
                failed_delivery += 1
                logger.warning(f"Final batch delivery failed - reviews will NOT be marked as processed")

        return {
            "analyzed": total_analyzed,
            "delivered": total_delivered,
            "marked_as_processed": total_marked,
            "failed_analysis": failed_analysis,
            "failed_delivery_batches": failed_delivery,
            "total": len(unprocessed_reviews),
            "batch_size": self.batch_size,
            "batches_sent": (total_delivered + self.batch_size - 1) // self.batch_size if total_delivered > 0 else 0,
            "message": f"Analyzed {total_analyzed}, delivered {total_delivered}, marked {total_marked} out of {len(unprocessed_reviews)} reviews"
        }

    async def _deliver_batch(
        self, 
        batch: List[ProcessedReview], 
        batch_ids: List[Tuple[str, str]]
    ) -> bool:
        """
        Доставляє батч відгуків і маркує їх як оброблені ТІЛЬКИ при успіху

        Args:
            batch: Список оброблених відгуків
            batch_ids: Список (source, id) для маркування

        Returns:
            bool: True якщо доставка і маркування успішні
        """
        try:
            # Спроба доставити
            await self.delivery_service.deliver_processed_reviews(batch)
            
            # Якщо доставка успішна - маркуємо як оброблені
            logger.info(f"Delivery successful, marking {len(batch_ids)} reviews as processed...")
            
            for source, review_id in batch_ids:
                await self.db_service.mark_as_processed(source, review_id)
            
            logger.info(f"Successfully marked {len(batch_ids)} reviews as processed")
            return True
            
        except Exception as e:
            logger.error(f"Batch delivery failed: {str(e)}")
            logger.error(f"Reviews in this batch will remain unprocessed and can be retried later")
            return False
