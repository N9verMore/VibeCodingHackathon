# ============================================
# FILE: pdmodule/models/review.py
# ============================================
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .enums import ReviewSource, Sentiment, Severity


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
    rating: Optional[int] = Field(None, ge=1, le=5)  # Optional для news
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
    categories: List[str]  # Масив категорій
    severity: Severity


class ProcessedReview(BaseModel):
    """Оброблений відгук"""
    id: str
    source: ReviewSource
    brand: str
    author: Optional[str] = None  # Автор відгуку
    backlink: str
    text: Optional[str]
    rating: Optional[int] = None  # Optional для news
    created_at: datetime
    sentiment: Sentiment
    description: str
    categories: List[str]  # Масив категорій
    severity: Severity
    is_processed: bool = True
