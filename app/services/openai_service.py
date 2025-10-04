# ============================================
# FILE: app/services/openai_service.py
# ============================================
import openai
import json
import logging
from fastapi import HTTPException
from app.models import ReviewFromDB, LLMAnalysis

logger = logging.getLogger(__name__)


class OpenAIService:
    """Сервіс для роботи з OpenAI API"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"OpenAIService initialized with model: {model}")

    async def analyze_review(self, review: ReviewFromDB) -> LLMAnalysis:
        """
        Аналізує відгук через OpenAI API

        Args:
            review: Відгук для аналізу

        Returns:
            LLMAnalysis: Результат аналізу
        """
        prompt = self._build_prompt(review)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            parsed = json.loads(result)

            return LLMAnalysis(
                sentiment=parsed["sentiment"],
                description=parsed["description"],
                category=parsed["category"]
            )

        except Exception as e:
            logger.error(f"OpenAI API error for review {review.id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI processing failed: {str(e)}"
            )

    def _get_system_prompt(self) -> str:
        """Системний промпт для LLM"""
        return """Ти - експерт з аналізу відгуків користувачів. 
Твоє завдання: визначити настрій відгуку, описати про що користувач пише, 
та категоризувати відгук.

Відповідай ТІЛЬКИ у форматі JSON:
{
  "sentiment": "позитивний|негативний|нейтральний",
  "description": "короткий опис того, на що скаржиться або що хвалить користувач",
  "category": "категорія (наприклад: оплата, інтерфейс, продуктивність, підтримка, функціональність тощо)"
}"""

    def _build_prompt(self, review: ReviewFromDB) -> str:
        """
        Будує промпт для аналізу відгуку

        Args:
            review: Відгук для аналізу

        Returns:
            str: Промпт для LLM
        """
        return f"""
Джерело: {review.source}
Оцінка: {review.rating}/5
Заголовок: {review.title or "Без заголовка"}
Текст відгуку: {review.text or "Без тексту"}
Дата створення: {review.created_at.isoformat()}

Проаналізуй цей відгук та поверни результат у JSON форматі.
"""
