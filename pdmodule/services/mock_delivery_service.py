import logging
from typing import List
from datetime import datetime
from pdmodule.models import ProcessedReview

logger = logging.getLogger(__name__)


class MockDeliveryService:
    """
    Mock сервіс для тестування доставки оброблених відгуків
    Замість відправки - виводить красиво форматовані результати
    """

    def __init__(self, endpoint: str = "mock"):
        self.endpoint = endpoint
        self.delivered_reviews = []  # Зберігаємо всі "доставлені" відгуки
        logger.info(f"MockDeliveryService initialized (TEST MODE)")

    async def deliver_processed_reviews(self, reviews: List[ProcessedReview]) -> bool:
        """
        "Доставляє" оброблені відгуки (виводить у консоль)

        Args:
            reviews: Список оброблених відгуків

        Returns:
            bool: True завжди (mock)
        """
        logger.info(f"\n{'=' * 80}")
        logger.info(f"📦 MOCK DELIVERY - Оброблені відгуки ({len(reviews)} шт.)")
        logger.info(f"{'=' * 80}\n")

        for idx, review in enumerate(reviews, 1):
            self._print_review(idx, review)
            self.delivered_reviews.append(review)

        logger.info(f"{'=' * 80}")
        logger.info(f"✅ Mock delivery completed: {len(reviews)} reviews")
        logger.info(f"{'=' * 80}\n")

        return True

    def _print_review(self, idx: int, review: ProcessedReview):
        """
        Виводить один відгук у зручному форматі
        """
        # Визначаємо емодзі для настрою
        sentiment_emoji = {
            "позитивний": "😊",
            "негативний": "😞",
            "нейтральний": "😐"
        }

        # Визначаємо емодзі для джерела
        source_emoji = {
            "appstore": "🍎",
            "googleplay": "🤖",
            "trustpilot": "⭐"
        }

        # Визначаємо емодзі для severity
        severity_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }

        # Кольорові індикатори рейтингу
        rating_stars = "⭐" * review.rating + "☆" * (5 - review.rating)

        logger.info(f"\n┌─ Відгук #{idx} ─────────────────────────────────────────────")
        logger.info(f"│")
        logger.info(f"│ 🆔 ID: {review.id}")
        logger.info(f"│ {source_emoji.get(review.source.value, '📱')} Джерело: {review.source.value.upper()}")
        logger.info(f"│ 🔗 Посилання: {review.backlink}")
        logger.info(f"│ 📅 Дата створення: {review.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"│")
        logger.info(f"│ {rating_stars} Рейтинг: {review.rating}/5")
        logger.info(f"│")
        logger.info(f"│ 📝 Текст відгуку:")
        logger.info(f"│    {self._wrap_text(review.text or 'Без тексту', 70)}")
        logger.info(f"│")
        logger.info(f"│ ─── 🤖 АНАЛІЗ LLM ───────────────────────────────────────")
        logger.info(f"│")
        logger.info(f"│ {sentiment_emoji.get(review.sentiment.value, '❓')} Настрій: {review.sentiment.value.upper()}")
        logger.info(f"│")
        logger.info(f"│ 🏷️  Категорії: {', '.join(review.categories)}")
        logger.info(f"│")
        logger.info(f"│ {severity_emoji.get(review.severity.value, '⚪')} Критичність: {review.severity.value.upper()}")
        logger.info(f"│")
        logger.info(f"│ 💭 Опис від LLM:")
        logger.info(f"│    {self._wrap_text(review.description, 70)}")
        logger.info(f"│")
        logger.info(f"└────────────────────────────────────────────────────────────\n")

    def _wrap_text(self, text: str, width: int) -> str:
        """
        Переносить текст на новий рядок з відступами
        """
        if not text:
            return ""

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n│    ".join(lines)

    def get_stats(self) -> dict:
        """
        Повертає статистику доставлених відгуків
        """
        if not self.delivered_reviews:
            return {
                "total_delivered": 0,
                "message": "No reviews delivered yet"
            }

        # Статистика по настрою
        sentiment_stats = {}
        for review in self.delivered_reviews:
            sentiment = review.sentiment.value
            sentiment_stats[sentiment] = sentiment_stats.get(sentiment, 0) + 1

        # Статистика по джерелах
        source_stats = {}
        for review in self.delivered_reviews:
            source = review.source.value
            source_stats[source] = source_stats.get(source, 0) + 1

        # Статистика по категоріях
        category_stats = {}
        for review in self.delivered_reviews:
            for category in review.categories:  # Тепер масив
                category_stats[category] = category_stats.get(category, 0) + 1

        # Статистика по severity
        severity_stats = {}
        for review in self.delivered_reviews:
            severity = review.severity.value
            severity_stats[severity] = severity_stats.get(severity, 0) + 1

        # Середній рейтинг
        avg_rating = sum(r.rating for r in self.delivered_reviews) / len(self.delivered_reviews)

        return {
            "total_delivered": len(self.delivered_reviews),
            "average_rating": round(avg_rating, 2),
            "sentiment_distribution": sentiment_stats,
            "source_distribution": source_stats,
            "category_distribution": category_stats,
            "severity_distribution": severity_stats,
            "delivered_ids": [r.id for r in self.delivered_reviews]
        }

    def get_all_delivered(self) -> List[dict]:
        """
        Повертає всі доставлені відгуки у вигляді списку словників
        """
        return [review.model_dump(mode='json') for review in self.delivered_reviews]

    def reset(self):
        """
        Очищає історію доставлених відгуків
        """
        self.delivered_reviews.clear()
        logger.info("Mock delivery history cleared")