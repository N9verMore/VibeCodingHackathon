# ============================================
# FILE: app/services/dynamodb_service.py
# ============================================
from typing import List
import logging
from app.models import ReviewFromDB

logger = logging.getLogger(__name__)


class DynamoDBService:
    """
    Сервіс для роботи з DynamoDB
    Реалізація від teammate
    """

    def __init__(self, table_name: str, region: str):
        self.table_name = table_name
        self.region = region
        # TODO: Ініціалізація boto3 client/resource
        logger.info(f"DynamoDBService initialized for table: {table_name}")

    async def get_unprocessed_reviews(self) -> List[ReviewFromDB]:
        """
        Отримує всі відгуки де isProcessed = False

        Returns:
            List[ReviewFromDB]: Список необроблених відгуків
        """
        # TODO: Реалізація від teammate
        # Приклад запиту:
        # response = table.scan(
        #     FilterExpression=Attr('isProcessed').eq(False)
        # )
        raise NotImplementedError("DynamoDB integration pending")

    async def mark_as_processed(self, review_id: str) -> bool:
        """
        Змінює isProcessed на True для конкретного відгуку

        Args:
            review_id: ID відгуку

        Returns:
            bool: True якщо успішно
        """
        # TODO: Реалізація від teammate
        # Приклад:
        # table.update_item(
        #     Key={'id': review_id},
        #     UpdateExpression='SET isProcessed = :val',
        #     ExpressionAttributeValues={':val': True}
        # )
        raise NotImplementedError("DynamoDB integration pending")

