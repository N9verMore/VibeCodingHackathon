from functools import lru_cache
from app.config import get_settings
from app.services import (
    DynamoDBService,
    OpenAIService,
    DeliveryService,
    ReviewProcessingService
)
from app.services.mock_dynamodb_service import MockDynamoDBService
from app.services.mock_delivery_service import MockDeliveryService


@lru_cache()
def get_dynamodb_service() -> DynamoDBService:
    """
    Dependency для DynamoDB сервісу

    Використовує MockDynamoDBService якщо USE_MOCK_DB=true в .env
    """
    settings = get_settings()

    # Перевіряємо чи використовувати mock
    if getattr(settings, 'use_mock_db', True):
        return MockDynamoDBService(
            table_name=settings.dynamodb_table_name,
            region=settings.aws_region
        )

    # Повертаємо реальний сервіс
    return DynamoDBService(
        table_name=settings.dynamodb_table_name,
        region=settings.aws_region
    )


@lru_cache()
def get_openai_service() -> OpenAIService:
    """Dependency для OpenAI сервісу"""
    settings = get_settings()
    return OpenAIService(
        api_key=settings.openai_api_key,
        model=settings.openai_model
    )


@lru_cache()
def get_delivery_service() -> DeliveryService:
    """
    Dependency для Delivery сервісу

    Використовує MockDeliveryService якщо USE_MOCK_DELIVERY=true в .env
    """
    settings = get_settings()

    # Перевіряємо чи використовувати mock
    if getattr(settings, 'use_mock_delivery', True):
        return MockDeliveryService(endpoint=settings.deliver_endpoint)

    # Повертаємо реальний сервіс
    return DeliveryService(endpoint=settings.deliver_endpoint)


@lru_cache()
def get_processing_service() -> ReviewProcessingService:
    """Dependency для Processing сервісу"""
    return ReviewProcessingService(
        db_service=get_dynamodb_service(),
        openai_service=get_openai_service(),
        delivery_service=get_delivery_service()
    )