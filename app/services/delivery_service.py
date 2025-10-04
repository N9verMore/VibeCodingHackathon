# ============================================
# FILE: app/services/delivery_service.py
# ============================================
import httpx
import logging
from typing import List
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
                response = await client.post(
                    self.endpoint,
                    json=[review.model_dump(mode='json') for review in reviews],
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
