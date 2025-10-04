# ============================================
# FILE: app/services/openai_service.py
# ============================================
import openai
import json
import logging
from typing import List
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

            # Fallback мапінг
            sentiment = self._normalize_sentiment(parsed["sentiment"])
            severity = self._normalize_severity(parsed["severity"])

            return LLMAnalysis(
                sentiment=sentiment,
                description=parsed["description"],
                categories=parsed["categories"],
                severity=severity
            )

        except Exception as e:
            logger.error(f"OpenAI API error for review {review.id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI processing failed: {str(e)}"
            )

    async def analyze_reviews_batch(self, reviews: List[ReviewFromDB]) -> List[LLMAnalysis]:
        """
        Аналізує кілька відгуків в одному запиті до OpenAI (batch)

        Args:
            reviews: Список відгуків для аналізу

        Returns:
            List[LLMAnalysis]: Список результатів аналізу
        """
        if not reviews:
            return []

        prompt = self._build_batch_prompt(reviews)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_batch_system_prompt()
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

            # Парсимо масив результатів
            analyses = []
            for item in parsed["reviews"]:
                # Fallback мапінг для sentiment (якщо LLM все ж таки відповів неправильно)
                sentiment = self._normalize_sentiment(item["sentiment"])
                # Fallback мапінг для severity
                severity = self._normalize_severity(item["severity"])

                analyses.append(LLMAnalysis(
                    sentiment=sentiment,
                    description=item["description"],
                    categories=item["categories"],
                    severity=severity
                ))

            # Перевіряємо що кількість результатів співпадає з кількістю відгуків
            if len(analyses) != len(reviews):
                logger.error(f"Batch analysis mismatch: expected {len(reviews)}, got {len(analyses)}")
                raise Exception(f"Batch analysis returned {len(analyses)} results for {len(reviews)} reviews")

            return analyses

        except Exception as e:
            logger.error(f"OpenAI Batch API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI batch processing failed: {str(e)}"
            )

    def _get_system_prompt(self) -> str:
        """Системний промпт для LLM"""
        return """Ти - експерт з аналізу відгуків користувачів. 
Твоє завдання: визначити настрій відгуку, описати про що користувач пише, 
категоризувати відгук та визначити рівень критичності.

Рівні критичності (severity):
- "low": Косметичні проблеми, побажання, дрібні незручності (колір кнопки, розмір шрифту, дизайн)
- "medium": Незручності в інтерфейсі, мінорні баги, повільна робота (складна навігація, повільне завантаження)
- "high": Серйозні проблеми що заважають роботі, втрата даних, проблеми з оплатою (не можу оплатити, втратив важливі дані)
- "critical": Критичні проблеми - креши, повна непрацездатність, проблеми безпеки (додаток крешить, не запускається, втратили всі дані)

Категорії (може бути кілька):
оплата, інтерфейс, продуктивність, підтримка, функціональність, баги, дизайн, безпека, стабільність, інше

КРИТИЧНО ВАЖЛИВО - Використовуй ТОЧНО ЦІ ЗНАЧЕННЯ:
- sentiment: ТІЛЬКИ 'позитивний' АБО 'негативний' АБО 'нейтральний' (українською мовою!)
- severity: ТІЛЬКИ 'low' АБО 'medium' АБО 'high' АБО 'critical' (англійською!)

Відповідай ТІЛЬКИ у форматі JSON:
{
  "sentiment": "позитивний",
  "description": "короткий опис того, на що скаржиться або що хвалить користувач",
  "categories": ["категорія1", "категорія2"],
  "severity": "low"
}"""

    def _get_batch_system_prompt(self) -> str:
        """Системний промпт для batch аналізу"""
        return """Ти - експерт з аналізу відгуків користувачів.
Твоє завдання: проаналізувати КІЛЬКА відгуків одночасно.

Для КОЖНОГО відгуку визнач:
- sentiment: позитивний/негативний/нейтральний
- description: короткий опис
- categories: масив категорій (оплата, інтерфейс, продуктивність, підтримка, функціональність, баги, дизайн, безпека, стабільність, інше)
- severity: low/medium/high/critical

Severity рівні:
- low: косметичні проблеми (колір, дизайн)
- medium: незручності в UI, мінорні баги
- high: серйозні проблеми (втрата даних, проблеми з оплатою)
- critical: креши, непрацездатність, проблеми безпеки

КРИТИЧНО ВАЖЛИВО - Використовуй ТОЧНО ЦІ ЗНАЧЕННЯ:
- sentiment: ТІЛЬКИ 'позитивний' АБО 'негативний' АБО 'нейтральний' (українською мовою!)
- severity: ТІЛЬКИ 'low' АБО 'medium' АБО 'high' АБО 'critical' (англійською!)

ВІДПОВІДАЙ ТІЛЬКИ у форматі JSON:
{
  "reviews": [
    {
      "sentiment": "позитивний",
      "description": "...",
      "categories": [...],
      "severity": "low"
    },
    ...
  ]
}

ДУЖЕ ВАЖЛИВО: Кількість об'єктів в масиві "reviews" МАЄ ТОЧНО співпадати з кількістю відгуків у запиті!
Поверни результат У ТОМУ Ж ПОРЯДКУ, як відгуки у запиті."""

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

    def _build_batch_prompt(self, reviews: List[ReviewFromDB]) -> str:
        """
        Будує batch промпт для кількох відгуків

        Args:
            reviews: Список відгуків

        Returns:
            str: Batch промпт
        """
        prompt_parts = [f"Проаналізуй {len(reviews)} відгуків та поверни результат у JSON форматі.\n"]

        for idx, review in enumerate(reviews, 1):
            prompt_parts.append(f"\n--- Відгук {idx} ---")
            prompt_parts.append(f"Джерело: {review.source.value}")
            prompt_parts.append(f"Оцінка: {review.rating}/5")
            if review.title:
                prompt_parts.append(f"Заголовок: {review.title}")
            prompt_parts.append(f"Текст: {review.text or 'Без тексту'}")
            prompt_parts.append(f"Дата: {review.created_at.isoformat()}")

        return "\n".join(prompt_parts)

    def _normalize_sentiment(self, sentiment: str) -> str:
        """
        Нормалізує sentiment до правильного формату (українською)
        
        Args:
            sentiment: Сирий sentiment від LLM
            
        Returns:
            str: Нормалізований sentiment
        """
        sentiment_lower = sentiment.lower().strip()

        # Мапінг різних варіантів на українські значення
        sentiment_map = {
            # Українська (правильна)
            "позитивний": "позитивний",
            "негативний": "негативний",
            "нейтральний": "нейтральний",
            # Англійська
            "positive": "позитивний",
            "negative": "негативний",
            "neutral": "нейтральний",
            # Іспанська
            "positivo": "позитивний",
            "negativo": "негативний",
            "neutro": "нейтральний",
            # Російська
            "позитивный": "позитивний",
            "негативный": "негативний",
            "нейтральный": "нейтральний",
        }

        result = sentiment_map.get(sentiment_lower)

        if result:
            if sentiment_lower != result:
                logger.warning(f"Normalized sentiment '{sentiment}' -> '{result}'")
            return result
        else:
            logger.error(f"Unknown sentiment value: '{sentiment}', defaulting to 'нейтральний'")
            return "нейтральний"

    def _normalize_severity(self, severity: str) -> str:
        """
        Нормалізує severity до правильного формату
        
        Args:
            severity: Сирий severity від LLM
            
        Returns:
            str: Нормалізований severity
        """
        severity_lower = severity.lower().strip()

        valid_severities = {"low", "medium", "high", "critical"}

        if severity_lower in valid_severities:
            return severity_lower
        else:
            logger.error(f"Unknown severity value: '{severity}', defaulting to 'medium'")
            return "medium"

    async def analyze_news(self, url: str) -> LLMAnalysis:
        """
        Аналізує новину за URL з використанням web search
        
        Args:
            url: URL новини
            
        Returns:
            LLMAnalysis: Результат аналізу
        """
        try:
            logger.info(f"Analyzing news from URL: {url}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_news_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": f"Проаналізуй новину за посиланням: {url}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = response.choices[0].message.content
            parsed = json.loads(result)

            sentiment = self._normalize_sentiment(parsed["sentiment"])
            severity = self._normalize_severity(parsed["severity"])

            return LLMAnalysis(
                sentiment=sentiment,
                description=parsed["description"],
                categories=parsed["categories"],
                severity=severity
            )

        except Exception as e:
            logger.error(f"OpenAI API error for news {url}: {str(e)}")
            raise Exception(f"Failed to analyze news: {str(e)}")

    def _get_news_system_prompt(self) -> str:
        """Системний промпт для аналізу новин"""
        return """Ти - експерт з аналізу новин про компанію/бренд.
Твоє завдання: прочитати новину за посиланням, визначити настрій, описати про що новина,
категоризувати та визначити рівень критичності для репутації бренду.

Рівні критичності (severity):
- "low": Нейтральна згадка, позитивна новина, незначні події
- "medium": Критика, скандал, негативні чутки
- "high": Серйозні звинувачення, проблеми з продуктом, втрата клієнтів
- "critical": Криза, судові позови, серйозні порушення, загроза бізнесу

Категорії (може бути кілька):
репутація, продукт, фінанси, юридичні, скандал, інновації, позитивні, партнерство, інше

КРИТИЧНО ВАЖЛИВО - Використовуй ТОЧНО ЦІ ЗНАЧЕННЯ:
- sentiment: ТІЛЬКИ 'позитивний' АБО 'негативний' АБО 'нейтральний' (українською мовою!)
- severity: ТІЛЬКИ 'low' АБО 'medium' АБО 'high' АБО 'critical' (англійською!)

Відповідай ТІЛЬКИ у форматі JSON:
{
  "sentiment": "позитивний",
  "description": "короткий опис про що новина та її вплив на репутацію бренду",
  "categories": ["категорія1", "категорія2"],
  "severity": "low"
}"""
