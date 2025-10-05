from openai import OpenAI
from app.config import settings
from typing import List, Dict
from app.models import ResponseTone, ResponseDraft
import json
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_response_drafts(
        self, 
        comment: str,
        brand_name: str,
        context: str,
        tones: List[ResponseTone],
        tone_adjustment: float = 0.5
    ) -> List[ResponseDraft]:
        """Генерує чернетки відповідей у різних стилях"""
        
        tone_descriptions = {
            ResponseTone.OFFICIAL: "Офіційний, професійний, формальний. Відповідь на 'Ви', без емоджі.",
            ResponseTone.FRIENDLY: "Дружній, неформальний, емпатійний. Можна використовувати 'ти', емоджі.",
            ResponseTone.TECH_SUPPORT: "Технічний, детальний, з конкретними кроками розв'язання проблеми."
        }
        
        tone_names = {
            ResponseTone.OFFICIAL: "official",
            ResponseTone.FRIENDLY: "friendly",
            ResponseTone.TECH_SUPPORT: "tech_support"
        }
        
        system_prompt = f"""Ти - експерт з customer support для бренду {brand_name}.
Твоє завдання - генерувати професійні відповіді на відгуки користувачів.

Контекст про бренд:
{context}

Tone adjustment: {tone_adjustment} (0=максимально оіційний, 1=максимально дружній)

Для кожного стилю згенеруй:
1. Текст відповіді (як жива людина, не робот!)
2. Action items (конкретні дії: refund, escalate, send_link, investigate, etc.)
3. Корисні посилання (якщо потрібно)

Відповідай українською мовою!
Відповідь має бути природною, емпатійною і корисною.
Не використовуй шаблонні фрази!"""

        # Формуємо опис стилів
        tones_text = "\n".join([
            f"- **{tone_names[tone]}**: {tone_descriptions[tone]}"
            for tone in tones
        ])

        user_prompt = f"""Відгук користувача:
\"\"\"
{comment}
\"\"\"

Згенеруй відповіді у таких стилях:
{tones_text}

ВАЖЛИВО: Відповідь має бути ПОВНОЮ і КОНКРЕТНОЮ!

Формат відповіді (JSON):
[
  {{
    "tone": "official/friendly/tech_support",
    "text": "ПОВНИЙ текст відповіді на відгук (3-5 речень)",
    "action_items": ["дія 1", "дія 2"],
    "suggested_links": ["посилання 1"]
  }}
]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI response: {content[:200]}...")  # Логуємо відповідь
            
            # Парсимо відповідь
            result = json.loads(content)
            
            # Якщо результат не список, а об'єкт з ключем
            if isinstance(result, dict):
                if "responses" in result:
                    result = result["responses"]
                elif "drafts" in result:
                    result = result["drafts"]
                else:
                    # Можливо це один об'єкт, обгорнемо в список
                    result = [result]
            
            drafts = []
            for item in result:
                # Перевіряємо чи є текст
                if not item.get("text") or item.get("text").strip() == "":
                    logger.warning(f"Empty text in response for tone {item.get('tone')}")
                    continue
                
                drafts.append(ResponseDraft(
                    tone=ResponseTone(item.get("tone", "official")),
                    text=item.get("text", ""),
                    action_items=item.get("action_items", []),
                    suggested_links=item.get("suggested_links", [])
                ))
            
            # Якщо не згенеровано жодної відповіді - використовуємо fallback
            if not drafts:
                logger.error("No valid drafts generated, using fallback")
                return self._get_fallback_responses(comment, brand_name, tones)
            
            return drafts
        
        except Exception as e:
            logger.error(f"Error generating responses: {e}")
            return self._get_fallback_responses(comment, brand_name, tones)
    
    def _get_fallback_responses(self, comment: str, brand_name: str, tones: List[ResponseTone]) -> List[ResponseDraft]:
        """Фолбек відповіді якщо OpenAI не спрацював"""
        import logging
        logger = logging.getLogger(__name__)
        
        fallback_texts = {
            ResponseTone.OFFICIAL: f"""Дякуємо за Ваш відгук про {brand_name}.

Ми цінуємо кожну думку наших користувачів і обов'язково розглянемо Ваше повідомлення. Наша команда працює над постійним покращенням якості сервісу.

Якщо у Вас виникли додаткові питання, будь ласка, зв'яжіться з нашою службою підтримки.

З повагою,
Команда {brand_name}""",
            
            ResponseTone.FRIENDLY: f"""Привіт! 👋

Дякуємо, що поділилися своїми враженнями про {brand_name}! Твоя думка дуже важлива для нас.

Ми завжди прагнемо стати кращими, тому обов'язково врахуємо твій фідбек. Якщо є ще якісь питання чи пропозиції - пиши, будемо раді допомогти! 😊

Дякуємо, що з нами!""",
            
            ResponseTone.TECH_SUPPORT: f"""Доброго дня!

Дякуємо за звернення щодо {brand_name}.

Для вирішення вашої проблеми, будь ласка:
1. Опишіть детальніше ситуацію
2. Вкажіть версію додатку/сервісу
3. Надішліть скріншот (якщо можливо)

Наша технічна підтримка готова допомогти вам у найкоротші терміни.

Очікуємо на вашу відповідь."""
        }
        
        drafts = []
        for tone in tones:
            drafts.append(ResponseDraft(
                tone=tone,
                text=fallback_texts.get(tone, fallback_texts[ResponseTone.OFFICIAL]),
                action_items=["Переслати в підтримку", "Розглянути вручну"],
                suggested_links=[]
            ))
        
        return drafts
    
    def answer_chat_query(self, query: str, context_data: dict) -> str:
        """Відповідає на запитання користувача про бренд"""
        
        system_prompt = """Ти - AI аналітик репутації бренду. 
Відповідай на запитання користувача на основі наданих даних про бренд.
Будь конкретним, використовуй цифри та факти.
Відповідай українською мовою."""

        # Формуємо контекст з даних
        context_summary = f"""
Дані про бренд:
- Всього згадувань: {context_data.get('total_mentions', 0)}
- Розподіл настроїв: {context_data.get('sentiment_distribution', {})}
- Топ категорії проблем: {context_data.get('top_categories', [])}
- Платформи: {context_data.get('platform_distribution', {})}

Релевантні коментарі:
{context_data.get('relevant_comments', 'Немає даних')}

База знань:
{context_data.get('knowledge_base', 'Немає даних')}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Контекст:\n{context_summary}\n\nЗапитання: {query}"}
                ],
                temperature=0.5
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Вибачте, сталася помилка при обробці запиту: {str(e)}"
    
    def analyze_crisis_severity(self, mentions: List[dict]) -> dict:
        """Аналізує серйозність кризи за допомогою LLM"""
        
        mentions_text = "\n".join([
            f"- [{m.get('platform')}] {m.get('body')[:100]}... (настрій: {m.get('sentiment')})"
            for m in mentions[:20]  # Беремо перші 20
        ])
        
        system_prompt = """Ти - експерт з кризового менеджменту репутації бренду.
Проаналізуй згадування та визнач:
1. Серйозність ситуації (low/medium/high/critical)
2. Основні теми проблем
3. Рекомендації для команди

Відповідай JSON."""

        user_prompt = f"""Аналіз {len(mentions)} згадувань бренду:

{mentions_text}

Формат відповіді:
{{
  "severity": "low/medium/high/critical",
  "main_topics": ["тема 1", "тема 2"],
  "recommendations": ["рекомендація 1", "рекомендація 2"],
  "summary": "короткий опис ситуації"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            return {
                "severity": "medium",
                "main_topics": ["Невідомо"],
                "recommendations": ["Проаналізувати ситуацію вручну"],
                "summary": f"Помилка аналізу: {str(e)}"
            }
    
    def generate_brand_comparison_answer(self, comparisons: List[dict]) -> str:
        """Генерує відповідь про порівняння брендів"""
        
        # Формуємо дані про кожен бренд
        brands_data = []
        for comp in comparisons:
            brands_data.append(f"""
**{comp['brand_name']}**:
- Згадувань: {comp['total_mentions']}
- Reputation Score: {comp['reputation_score']}/100
- Sentiment: позитив {comp['sentiment_distribution']['positive']}, негатив {comp['sentiment_distribution']['negative']}, нейтрал {comp['sentiment_distribution']['neutral']}
- Severity: critical {comp['severity_distribution']['critical']}, high {comp['severity_distribution']['high']}, medium {comp['severity_distribution']['medium']}, low {comp['severity_distribution']['low']}

Сильні сторони:
{chr(10).join(['- ' + s for s in comp['top_strengths']])}

Слабкі сторони:
{chr(10).join(['- ' + w for w in comp['top_weaknesses']])}
""")
        
        system_prompt = """Ти - експерт з аналізу репутації брендів.
Порівняй бренди на основі наданих даних.

Відповідай простою мовою, зрозуміло.

Структура відповіді:
1. Почни з чіткого висновку: "Який бренд кращий і чому"
2. Порівняння по ключових метриках (reputation score, sentiment, критичність)
3. Сильні сторони кожного бренду
4. Слабкі сторони кожного бренду
5. Загальний висновок і рекомендації

Використовуй емоджі для наочності.
Відповідай українською."""
        
        user_prompt = f"""Порівняй ці бренди:

{chr(10).join(brands_data)}

Зроби детальний аналіз і порівняння."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            # Fallback - просте порівняння
            result = "# 📊 Порівняння брендів\n\n"
            
            # Сортуємо за reputation score
            sorted_brands = sorted(comparisons, key=lambda x: x['reputation_score'], reverse=True)
            
            result += f"## 🏆 Переможець: {sorted_brands[0]['brand_name']}\n\n"
            result += f"**{sorted_brands[0]['brand_name']}** має кращу репутацію ({sorted_brands[0]['reputation_score']}/100)\n\n"
            
            for brand in sorted_brands:
                result += f"### {brand['brand_name']}\n"
                result += f"- Reputation: {brand['reputation_score']}/100\n"
                result += f"- Згадувань: {brand['total_mentions']}\n\n"
            
            return result

    def analyze_negative_spike(self, negative_comments: List[dict], increase_ratio: float) -> dict:
        """Аналіз сплеску негативних згадок"""
        
        comments_text = "\n".join([
            f"- [{c.get('platform')}] {c.get('body')[:150]}..."
            for c in negative_comments[:15]
        ])
        
        system_prompt = """Ти - експерт з кризового менеджменту репутації.
Проаналізуй сплеск негативних згадок і дай:
1. Коротке резюме (2-3 речення)
2. Основні проблеми
3. Рекомендації для команди

Відповідай JSON."""
        
        user_prompt = f"""Збільшення негативу: {increase_ratio:.1f}x

Негативні згадки:
{comments_text}

Формат:
{{
  "summary": "коротке резюме",
  "main_issues": ["проблема 1", "проблема 2"],
  "recommendations": ["рекомендація 1", "рекомендація 2"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            return {
                "summary": f"Виявлено збільшення негативних згадок у {increase_ratio:.1f} разів. Потрібна увага.",
                "main_issues": ["Невідомо"],
                "recommendations": ["Проаналізувати вручну"]
            }


# Singleton
openai_service = OpenAIService()
