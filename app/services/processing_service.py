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
            delivery_service: DeliveryService
    ):
        self.db_service = db_service
        self.openai_service = openai_service
        self.delivery_service = delivery_service
        logger.info("ReviewProcessingService initialized")

    async def process_reviews(self) -> Dict:
        """
        Основний метод обробки відгуків

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

        # 2. Обробляємо кожен відгук через OpenAI
        processed_reviews = []

        for review in unprocessed_reviews:
            try:
                logger.info(f"Processing review {review.id}...")

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
                    isProcessed=True
                )

                processed_reviews.append(processed_review)

                # Оновлюємо статус в БД
                await self.db_service.mark_as_processed(review.id)
                logger.info(f"Review {review.id} processed successfully")

            except Exception as e:
                logger.error(f"Failed to process review {review.id}: {str(e)}")
                continue

        # 3. Відправляємо оброблені відгуки
        if processed_reviews:
            await self.delivery_service.deliver_processed_reviews(processed_reviews)

        return {
            "processed": len(processed_reviews),
            "total": len(unprocessed_reviews),
            "message": f"Successfully processed {len(processed_reviews)} out of {len(unprocessed_reviews)} reviews"
        }
