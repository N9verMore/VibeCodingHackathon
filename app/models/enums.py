# ============================================
# FILE: app/models/enums.py
# ============================================
from enum import Enum


class ReviewSource(str, Enum):
    """Джерела відгуків"""
    appstore = "appstore"
    googleplay = "googleplay"
    trustpilot = "trustpilot"


class Sentiment(str, Enum):
    """Настрій відгуку"""
    positive = "позитивний"
    negative = "негативний"
    neutral = "нейтральний"
