from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    """Платформи для відгуків"""
    APP_STORE = "app_store"
    APPSTORE = "appstore"  # Додаємо альтернативне написання
    GOOGLE_PLAY = "google_play"
    GOOGLEPLAY = "googleplay"  # Додаємо альтернативне написання
    TRUSTPILOT = "trustpilot"
    REDDIT = "reddit"
    QUORA = "quora"
    GOOGLE_SERP = "google_serp"
    INSTAGRAM = "instagram"


class Sentiment(str, Enum):
    """Тип настрою"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    # Додаємо українські варіанти
    POZYTYVNYI = "позитивний"
    NEHATYVNYI = "негативний"
    NEITRALNYI = "нейтральний"


class IntentType(str, Enum):
    """Тип наміру користувача"""
    COMPLAINT = "complaint"
    QUESTION = "question"
    RECOMMENDATION = "recommendation"
    NEUTRAL_MENTION = "neutral_mention"


class ResponseTone(str, Enum):
    """Тон відповіді"""
    OFFICIAL = "official"
    FRIENDLY = "friendly"
    TECH_SUPPORT = "tech_support"


class CrisisLevel(str, Enum):
    """Рівень кризи"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CommentInput(BaseModel):
    """Вхідні дані для коментаря/відгуку"""
    brand_name: str = Field(..., description="Назва бренду")
    body: str = Field(..., description="Текст коментаря")
    author: Optional[str] = Field(None, description="Автор коментаря")
    timestamp: datetime = Field(..., description="Час коментаря")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Оцінка від 0 до 5")
    backlink: Optional[str] = Field(None, description="Посилання на коментар")
    platform: Platform = Field(..., description="Платформа")
    sentiment: Sentiment = Field(..., description="Настрій")
    llm_description: Optional[str] = Field(None, description="Опис від LLM")
    category: Optional[str] = Field(None, description="Категорія (payment, interface, etc.)")
    severity: Optional[str] = Field(None, description="Рівень серйозності (low, medium, high, critical)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand_name": "Zara",
                "body": "Додаток постійно вилітає під час оплати!",
                "author": "JohnDoe123",
                "timestamp": "2025-10-04T14:30:00",
                "rating": 1.0,
                "backlink": "https://apps.apple.com/review/123",
                "platform": "app_store",
                "sentiment": "negative",
                "llm_description": "Користувач скаржиться на краш додатку при оплаті",
                "category": "payment_crash",
                "severity": "high"
            }
        }


# НОВИЙ формат для вашого API
class ExternalReview(BaseModel):
    """Формат відгуку з вашого API"""
    id: str
    brand: str = Field(..., description="Назва бренду")
    source: str  # appstore, googleplay, trustpilot, google_search
    backlink: str
    text: str
    author: Optional[str] = Field(None, description="Автор відгуку")
    rating: Optional[int] = None  # Опціонально для google_search
    created_at: str  # ISO format datetime
    sentiment: str  # позитивний, негативний, нейтральний
    description: str
    categories: List[str]  # Масив категорій
    severity: Literal["low", "medium", "high", "critical"]  # Рівень серйозності
    is_processed: bool = True


class ExternalReviewsBatch(BaseModel):
    """Пакет відгуків з вашого API"""
    reviews: List[ExternalReview]
    count: int


class DocumentInput(BaseModel):
    """Вхідні дані для довільного документа"""
    title: str = Field(..., description="Назва документа")
    content: str = Field(..., description="Вміст документа")
    doc_type: str = Field(default="general", description="Тип документа")
    metadata: Optional[dict] = Field(default_factory=dict)


class SearchResultInput(BaseModel):
    """Результати з Google SERP"""
    query: str = Field(..., description="Пошуковий запит")
    title: str = Field(..., description="Заголовок результату")
    snippet: str = Field(..., description="Snippet з пошуку")
    url: str = Field(..., description="URL")
    position: int = Field(..., description="Позиція в видачі")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatMessage(BaseModel):
    """Повідомлення в чаті"""
    message: str = Field(..., description="Запитання користувача")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Які найпоширеніші скарги на Zara?"
            }
        }


class ResponseDraft(BaseModel):
    """Чернетка відповіді"""
    tone: ResponseTone
    text: str
    action_items: List[str] = Field(default_factory=list)
    suggested_links: List[str] = Field(default_factory=list)


class GenerateResponseRequest(BaseModel):
    """Запит на генерацію відповіді"""
    comment_id: str
    tones: List[ResponseTone] = Field(default=[ResponseTone.OFFICIAL, ResponseTone.FRIENDLY, ResponseTone.TECH_SUPPORT])
    tone_adjustment: Optional[float] = Field(default=0.5, ge=0, le=1, description="0=строго офіційний, 1=максимально дружній")


class CrisisAlert(BaseModel):
    """Сповіщення про кризу"""
    crisis_level: CrisisLevel
    platform: Optional[Platform]
    description: str
    affected_count: int
    critical_keywords: List[str]
    timestamp: datetime
    recommendations: List[str]


class ReputationScore(BaseModel):
    """Загальна оцінка репутації"""
    overall_score: float = Field(..., ge=0, le=100)
    trend: Literal["up", "down", "stable"]
    risk_level: CrisisLevel
    platform_scores: dict
    last_updated: datetime


class StatisticsResponse(BaseModel):
    """Статистика по бренду"""
    total_mentions: int
    sentiment_distribution: dict
    platform_distribution: dict
    average_rating: Optional[float]
    top_categories: List[dict]
    timeline_data: List[dict]
    reputation_score: ReputationScore
    severity_distribution: Optional[dict] = None  # Додаємо розподіл по severity


class StatisticsFilters(BaseModel):
    """Фільтри для статистики"""
    brand_name: Optional[str] = Field(
        None,
        description="Фільтр по бренду"
    )
    date_from: Optional[str] = Field(
        None,
        description="Дата від (ISO format)"
    )
    date_to: Optional[str] = Field(
        None,
        description="Дата до (ISO format)"
    )
    platforms: Optional[List[str]] = Field(
        None,
        description="Фільтр по платформах"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand_name": "Zara",
                "date_from": "2025-10-01T00:00:00",
                "date_to": "2025-10-04T23:59:59",
                "platforms": ["app_store", "google_play"]
            }
        }


class ReviewFilters(BaseModel):
    """Фільтри для пошуку відгуків"""
    brand_name: Optional[str] = Field(
        None,
        description="Фільтр по бренду"
    )
    severity: Optional[List[Literal["low", "medium", "high", "critical"]]] = Field(
        None,
        description="Фільтр по рівню серйозності"
    )
    sentiment: Optional[List[Literal["positive", "negative", "neutral"]]] = Field(
        None,
        description="Фільтр по настрою"
    )
    categories: Optional[List[str]] = Field(
        None,
        description="Фільтр по категоріях (ANY - хоча б одна збігається)"
    )
    platforms: Optional[List[str]] = Field(
        None,
        description="Фільтр по платформах"
    )
    rating_min: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Мінімальний рейтинг"
    )
    rating_max: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Максимальний рейтинг"
    )
    date_from: Optional[str] = Field(
        None,
        description="Дата від (ISO format)"
    )
    date_to: Optional[str] = Field(
        None,
        description="Дата до (ISO format)"
    )
    limit: Optional[int] = Field(
        100,
        ge=1,
        le=1000,
        description="Максимальна кількість результатів"
    )
    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Зміщення для пагінації"
    )
    sort_by: Optional[Literal["timestamp", "rating", "severity"]] = Field(
        "timestamp",
        description="Сортування"
    )
    sort_order: Optional[Literal["asc", "desc"]] = Field(
        "desc",
        description="Порядок сортування"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand_name": "Zara",
                "severity": ["high", "critical"],
                "sentiment": ["negative"],
                "categories": ["оплата", "краш"],
                "platforms": ["app_store", "google_play"],
                "rating_min": 1.0,
                "rating_max": 2.0,
                "date_from": "2025-10-01T00:00:00",
                "date_to": "2025-10-04T23:59:59",
                "limit": 50,
                "offset": 0,
                "sort_by": "severity",
                "sort_order": "desc"
            }
        }


class BrandComparisonRequest(BaseModel):
    """Запит на порівняння брендів"""
    brand_names: List[str] = Field(..., min_length=2, max_length=5, description="Список брендів для порівняння")
    date_from: Optional[str] = Field(None, description="Дата від")
    date_to: Optional[str] = Field(None, description="Дата до")
    
    class Config:
        json_schema_extra = {
            "example": {
                "brand_names": ["Zara", "H&M", "Mango"],
                "date_from": "2025-09-01T00:00:00",
                "date_to": "2025-10-04T23:59:59"
            }
        }


class BrandComparison(BaseModel):
    """Порівняння брендів"""
    brand_name: str
    total_mentions: int
    reputation_score: float
    sentiment_distribution: dict
    severity_distribution: dict
    top_strengths: List[str]
    top_weaknesses: List[str]
    platform_performance: dict
