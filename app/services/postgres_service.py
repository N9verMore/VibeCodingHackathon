# ============================================
# FILE: app/services/postgres_service.py
# ============================================
import logging
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, Text, ARRAY, select
from sqlalchemy.orm import declarative_base
from app.models import ProcessedReview

logger = logging.getLogger(__name__)

Base = declarative_base()


class ProcessedReviewDB(Base):
    """Модель таблиці для оброблених відгуків"""
    __tablename__ = 'processed_reviews'

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    backlink = Column(Text, nullable=False)
    text = Column(Text)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    # LLM Analysis
    sentiment = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    categories = Column(ARRAY(String), nullable=False)  # Масив категорій
    severity = Column(String, nullable=False)
    
    # Метадані
    is_processed = Column(String, default='true')
    processed_at = Column(DateTime, default=datetime.utcnow)


class PostgresService:
    """Сервіс для роботи з PostgreSQL"""

    def __init__(self, database_url: str):
        # Конвертуємо postgresql:// в postgresql+psycopg://
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("PostgresService initialized")

    async def init_db(self):
        """Створює таблиці якщо їх немає"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    async def save_processed_reviews(self, reviews: List[ProcessedReview]) -> dict:
        """
        Зберігає список оброблених відгуків в PostgreSQL

        Args:
            reviews: Список оброблених відгуків

        Returns:
            dict: Статистика збереження
        """
        if not reviews:
            return {"saved": 0, "failed": 0}

        success_count = 0
        failed_count = 0

        try:
            async with self.async_session() as session:
                for review in reviews:
                    try:
                        db_review = ProcessedReviewDB(
                            id=review.id,
                            source=review.source.value,
                            backlink=review.backlink,
                            text=review.text,
                            rating=review.rating,
                            created_at=review.created_at,
                            sentiment=review.sentiment.value,
                            description=review.description,
                            categories=review.categories,  # PostgreSQL ARRAY
                            severity=review.severity.value,
                            is_processed='true',
                            processed_at=datetime.utcnow()
                        )
                        
                        session.add(db_review)
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to prepare review {review.id}: {str(e)}")
                        failed_count += 1
                        continue

                # Commit всіх разом
                await session.commit()
                logger.info(f"Successfully saved {success_count} reviews to PostgreSQL")

        except Exception as e:
            logger.error(f"Failed to save reviews to PostgreSQL: {str(e)}")
            return {"saved": 0, "failed": len(reviews)}

        return {
            "saved": success_count,
            "failed": failed_count,
            "total": len(reviews)
        }

    async def get_review_by_id(self, review_id: str) -> ProcessedReviewDB:
        """Отримує відгук за ID"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(ProcessedReviewDB).where(ProcessedReviewDB.id == review_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get review {review_id}: {str(e)}")
            return None

    async def get_stats(self) -> dict:
        """Отримує статистику з PostgreSQL"""
        try:
            async with self.async_session() as session:
                # Загальна кількість
                result = await session.execute(
                    select(ProcessedReviewDB.id)
                )
                total = len(result.all())

                return {
                    "total_in_postgres": total,
                    "status": "connected"
                }
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {
                "total_in_postgres": 0,
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Закриває з'єднання"""
        await self.engine.dispose()
        logger.info("PostgreSQL connection closed")
