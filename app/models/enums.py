# ============================================
# FILE: app/models/enums.py
# ============================================
from enum import Enum


class ReviewSource(str, Enum):
    """Джерела відгуків"""
    appstore = "appstore"
    googleplay = "googleplay"
    trustpilot = "trustpilot"
    news = "news"
    instagram = "instagram"
    reddit = "reddit"
    


class Sentiment(str, Enum):
    """Настрій відгуку"""
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class Severity(str, Enum):
    """Рівень критичності відгуку"""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
