# ============================================
# FILE: app/services/delivery_service.py
# ============================================
import httpx
import logging
from typing import List
from datetime import datetime
from fastapi import HTTPException
from app.models import ProcessedReview

logger = logging.getLogger(__name__)


class DeliveryService:
    """Сервіс для доставки оброблених відгуків"""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        logger.info(f"DeliveryService initialized with endpoint: {endpoint}")

    async def deliver_processed_reviews(self, reviews: List[ProcessedReview]) -> bool:
        """
        Відправляє оброблені відгуки на POST /deliver_processed

        Args:
            reviews: Список оброблених відгуків

        Returns:
            bool: True якщо успішно
        """
        async with httpx.AsyncClient() as client:
            try:
                # Підготовка даних у потрібному форматі
                reviews_data = []
                for review in reviews:
                    review_dict = review.model_dump(mode='json')
                    # Перетворюємо enum в string
                    review_dict['source'] = review.source.value
                    review_dict['sentiment'] = review.sentiment.value
                    review_dict['severity'] = review.severity.value  # Нове поле
                    # Перетворюємо datetime в ISO string
                    if isinstance(review_dict.get('created_at'), datetime):
                        review_dict['created_at'] = review.created_at.isoformat()
                    # categories вже масив, нічого не робимо
                    reviews_data.append(review_dict)
                
                # Формуємо payload як очікує teammate
                payload = {
                    "reviews": reviews_data,
                    "count": len(reviews_data)
                }
                
                logger.info(f"Sending batch of {len(reviews)} reviews to {self.endpoint}")
                
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Successfully delivered {len(reviews)} processed reviews via HTTP")
                return True
            except Exception as e:
                logger.error(f"Failed to deliver reviews via HTTP: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Delivery failed: {str(e)}"
                )
