# ============================================
# FILE: app/models/review.py
# ============================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import ReviewSource, Sentiment


class ReviewFromDB(BaseModel):
    """Модель відгуку з бази даних"""
    id: str
    source: ReviewSource
    backlink: str
    brand: str
    is_processed: bool
    app_identifier: str
    title: Optional[str] = None
    text: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    language: str
    country: Optional[str] = None
    author_hint: Optional[str] = None
    created_at: datetime
    fetched_at: datetime
    content_hash: str


class LLMAnalysis(BaseModel):
    """Результат аналізу LLM"""
    sentiment: Sentiment
    description: str
    category: str


class ProcessedReview(BaseModel):
    """Оброблений відгук"""
    id: str
    source: ReviewSource
    backlink: str
    text: Optional[str]
    rating: int
    created_at: datetime
    sentiment: Sentiment
    description: str
    category: str
    is_processed: bool = True