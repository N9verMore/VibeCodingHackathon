# ============================================
# FILE: app/services/processing_service.py
# ============================================
import logging
from typing import Dict
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
        processed_reviews = []
        current_batch = []
        total_processed = 0
        total_delivered = 0

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
                processed_reviews.append(processed_review)
                total_processed += 1

                # Оновлюємо статус в БД
                await self.db_service.mark_as_processed(review.source, review.id)
                logger.info(f"Review {review.id} processed successfully")

                # Перевіряємо чи заповнився батч
                if len(current_batch) >= self.batch_size:
                    logger.info(f"Batch of {len(current_batch)} reviews ready, delivering...")
                    await self.delivery_service.deliver_processed_reviews(current_batch)
                    total_delivered += len(current_batch)
                    logger.info(f"Batch delivered successfully ({total_delivered}/{total_processed} delivered so far)")
                    current_batch = []  # Очищаємо батч

            except Exception as e:
                logger.error(f"Failed to process review {review.id}: {str(e)}")
                continue

        # 3. Відправляємо залишок (якщо є неповний батч)
        if current_batch:
            logger.info(f"Delivering final batch of {len(current_batch)} reviews...")
            await self.delivery_service.deliver_processed_reviews(current_batch)
            total_delivered += len(current_batch)
            logger.info(f"Final batch delivered ({total_delivered} total delivered)")

        return {
            "processed": total_processed,
            "delivered": total_delivered,
            "total": len(unprocessed_reviews),
            "batch_size": self.batch_size,
            "batches_sent": (total_delivered + self.batch_size - 1) // self.batch_size,  # ceiling division
            "message": f"Successfully processed {total_processed} out of {len(unprocessed_reviews)} reviews, delivered in batches of {self.batch_size}"
        }
