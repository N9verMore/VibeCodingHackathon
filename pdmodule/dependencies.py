from functools import lru_cache
from pdmodule.config import get_settings
from pdmodule.services import (
    DynamoDBService,
    OpenAIService,
    DeliveryService,
    ReviewProcessingService
)
from pdmodule.services.mock_dynamodb_service import MockDynamoDBService
from pdmodule.services.mock_delivery_service import MockDeliveryService


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

    # Повертаємо реальний сервіс з credentials
    return DynamoDBService(
        table_name=settings.dynamodb_table_name,
        region=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None
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
        return MockDeliveryService(
            endpoint=settings.deliver_endpoint
        )

    # Повертаємо реальний сервіс
    return DeliveryService(
        endpoint=settings.deliver_endpoint
    )


@lru_cache()
def get_processing_service() -> ReviewProcessingService:
    """Dependency для Processing сервісу"""
    settings = get_settings()
    return ReviewProcessingService(
        db_service=get_dynamodb_service(),
        openai_service=get_openai_service(),
        delivery_service=get_delivery_service(),
        batch_size=settings.batch_size
    )
