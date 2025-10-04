from fastapi import APIRouter, BackgroundTasks, Depends
from datetime import datetime
from app.services import ReviewProcessingService
from app.dependencies import get_processing_service, get_dynamodb_service, get_delivery_service
from app.services.mock_dynamodb_service import MockDynamoDBService
from app.services.mock_delivery_service import MockDeliveryService

router = APIRouter()


@router.post("/process-reviews")
async def trigger_review_processing(
    background_tasks: BackgroundTasks,
    service: ReviewProcessingService = Depends(get_processing_service)
):
    """
    Запустити обробку відгуків у фоновому режимі
    """
    background_tasks.add_task(service.process_reviews)
    return {"message": "Review processing started"}


@router.post("/process-reviews-sync")
async def process_reviews_sync(
    service: ReviewProcessingService = Depends(get_processing_service)
):
    """
    Синхронна обробка відгуків (для тестування)
    """
    result = await service.process_reviews()
    return result


# ==================== MOCK DB ENDPOINTS ====================

@router.post("/mock/db/reset")
async def reset_mock_db_data(
    db_service = Depends(get_dynamodb_service)
):
    """
    Скидає оброблені mock відгуки (тільки для MockDynamoDBService)
    """
    if isinstance(db_service, MockDynamoDBService):
        db_service.reset_processed()
        return {"message": "Mock DB data reset successfully"}
    else:
        return {"error": "This endpoint only works with MockDynamoDBService"}


@router.get("/mock/db/stats")
async def get_mock_db_stats(
    db_service = Depends(get_dynamodb_service)
):
    """
    Отримати статистику mock БД (тільки для MockDynamoDBService)
    """
    if isinstance(db_service, MockDynamoDBService):
        return db_service.get_stats()
    else:
        return {"error": "This endpoint only works with MockDynamoDBService"}


# ==================== MOCK DELIVERY ENDPOINTS ====================

@router.get("/mock/delivery/stats")
async def get_mock_delivery_stats(
    delivery_service = Depends(get_delivery_service)
):
    """
    Отримати статистику доставлених відгуків (тільки для MockDeliveryService)
    """
    if isinstance(delivery_service, MockDeliveryService):
        return delivery_service.get_stats()
    else:
        return {"error": "This endpoint only works with MockDeliveryService"}


@router.get("/mock/delivery/all")
async def get_all_delivered_reviews(
    delivery_service = Depends(get_delivery_service)
):
    """
    Отримати всі доставлені відгуки (тільки для MockDeliveryService)
    """
    if isinstance(delivery_service, MockDeliveryService):
        return {
            "reviews": delivery_service.get_all_delivered(),
            "count": len(delivery_service.delivered_reviews)
        }
    else:
        return {"error": "This endpoint only works with MockDeliveryService"}


@router.post("/mock/delivery/reset")
async def reset_mock_delivery(
    delivery_service = Depends(get_delivery_service)
):
    """
    Очистити історію доставлених відгуків (тільки для MockDeliveryService)
    """
    if isinstance(delivery_service, MockDeliveryService):
        delivery_service.reset()
        return {"message": "Mock delivery history cleared"}
    else:
        return {"error": "This endpoint only works with MockDeliveryService"}


# ==================== GENERAL ENDPOINTS ====================

@router.get("/health")
async def health_check(
    db_service = Depends(get_dynamodb_service),
    delivery_service = Depends(get_delivery_service)
):
    """Перевірка стану сервісу"""
    return {
        "status": "healthy",
        "service": "review-processor",
        "db_mode": "mock" if isinstance(db_service, MockDynamoDBService) else "production",
        "delivery_mode": "mock" if isinstance(delivery_service, MockDeliveryService) else "production",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/")
async def root():
    """Інформація про API"""
    return {
        "service": "Brand Reputation Defender - Review Processor",
        "version": "1.0.0",
        "endpoints": {
            "processing": {
                "POST /process-reviews": "Запустити обробку відгуків (асинхронно)",
                "POST /process-reviews-sync": "Запустити обробку відгуків (синхронно)"
            },
            "mock_db": {
                "POST /mock/db/reset": "Скинути оброблені mock відгуки",
                "GET /mock/db/stats": "Статистика mock БД"
            },
            "mock_delivery": {
                "GET /mock/delivery/stats": "Статистика доставлених відгуків",
                "GET /mock/delivery/all": "Всі доставлені відгуки (JSON)",
                "POST /mock/delivery/reset": "Очистити історію доставки"
            },
            "general": {
                "GET /health": "Перевірка стану сервісу",
                "GET /": "Інформація про API"
            }
        }
    }