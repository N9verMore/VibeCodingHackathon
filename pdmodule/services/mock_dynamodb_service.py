from typing import List, Optional
import logging
from datetime import datetime, timedelta
from pdmodule.models import ReviewFromDB, ReviewSource

logger = logging.getLogger(__name__)


class MockDynamoDBService:
    """
    Mock сервіс для тестування обробки відгуків
    Повертає фейкові коментарі для перевірки роботи
    """

    def __init__(self, table_name: str = "mock", region: str = "mock"):
        self.table_name = table_name
        self.region = region
        self.processed_ids = set()  # Зберігаємо ID оброблених відгуків
        logger.info(f"MockDynamoDBService initialized (TEST MODE)")

    async def get_unprocessed_reviews(self, brand: Optional[str] = None) -> List[ReviewFromDB]:
        """
        Повертає фейкові необроблені відгуки для тестування

        Returns:
            List[ReviewFromDB]: Список тестових відгуків
        """
        logger.info("Returning mock reviews for testing")

        now = datetime.utcnow()

        mock_reviews = [
            # Позитивний відгук - App Store
            ReviewFromDB(
                id="review_001",
                source=ReviewSource.appstore,
                backlink="https://apps.apple.com/review/001",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Чудовий додаток!",
                text="Користуюся вже місяць, все працює відмінно. Інтерфейс зручний, швидко завантажується. Особливо подобається функція автоматичного збереження.",
                rating=5,
                language="uk",
                country="UA",
                author_hint="Андрій К.",
                created_at=now - timedelta(days=2),
                fetched_at=now - timedelta(hours=1),
                content_hash="hash_001"
            ),

            # Негативний відгук - Google Play (проблема з оплатою)
            ReviewFromDB(
                id="review_002",
                source=ReviewSource.googleplay,
                backlink="https://play.google.com/review/002",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Не можу оплатити підписку",
                text="Намагаюся оплатити преміум підписку, але постійно вилітає помилка. Підтримка не відповідає вже 3 дні. Дуже розчарований.",
                rating=1,
                language="uk",
                country="UA",
                author_hint="user_1234",
                created_at=now - timedelta(days=1),
                fetched_at=now - timedelta(hours=2),
                content_hash="hash_002"
            ),

            # Нейтральний відгук - Trustpilot
            ReviewFromDB(
                id="review_003",
                source=ReviewSource.trustpilot,
                backlink="https://trustpilot.com/review/003",
                brand="TestBrand",
                is_processed=False,
                app_identifier="testbrand-business-unit",
                title="Нормально, але є над чим працювати",
                text="Загалом додаток робочий. Є деякі баги, наприклад іноді не синхронізуються дані. Але в цілому функціонал задовольняє базові потреби.",
                rating=3,
                language="uk",
                country="UA",
                author_hint="Олена",
                created_at=now - timedelta(hours=12),
                fetched_at=now - timedelta(minutes=30),
                content_hash="hash_003"
            ),

            # Негативний відгук - App Store (проблема з інтерфейсом)
            ReviewFromDB(
                id="review_004",
                source=ReviewSource.appstore,
                backlink="https://apps.apple.com/review/004",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Незрозумілий інтерфейс",
                text="Після останнього оновлення все переплуталось. Не можу знайти де налаштування. Кнопки маленькі, важко натискати на телефоні. Верніть стару версію!",
                rating=2,
                language="uk",
                country="UA",
                author_hint="Марія В.",
                created_at=now - timedelta(hours=6),
                fetched_at=now - timedelta(minutes=15),
                content_hash="hash_004"
            ),

            # Позитивний відгук - Google Play (продуктивність)
            ReviewFromDB(
                id="review_005",
                source=ReviewSource.googleplay,
                backlink="https://play.google.com/review/005",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Швидко і стабільно",
                text="Оновлення дійсно покращило швидкість роботи. Тепер все летить! Навіть на старому телефоні працює без лагів. Молодці розробники!",
                rating=5,
                language="uk",
                country="UA",
                author_hint="Дмитро",
                created_at=now - timedelta(hours=3),
                fetched_at=now - timedelta(minutes=5),
                content_hash="hash_005"
            ),

            # Негативний відгук - Trustpilot (підтримка)
            ReviewFromDB(
                id="review_006",
                source=ReviewSource.trustpilot,
                backlink="https://trustpilot.com/review/006",
                brand="TestBrand",
                is_processed=False,
                app_identifier="testbrand-business-unit",
                title="Жахлива підтримка",
                text="Написав в підтримку тиждень тому - досі ніякої відповіді. В чаті бот, який не розуміє питання. Телефону немає. Як з вами зв'язатись???",
                rating=1,
                language="uk",
                country="UA",
                author_hint="Сергій М.",
                created_at=now - timedelta(days=7),
                fetched_at=now - timedelta(hours=3),
                content_hash="hash_006"
            ),

            # Позитивний відгук - App Store (функціональність)
            ReviewFromDB(
                id="review_007",
                source=ReviewSource.appstore,
                backlink="https://apps.apple.com/review/007",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Всі функції що потрібно",
                text="Нарешті додаток, в якому є все необхідне. Особливо круто що додали експорт в PDF та інтеграцію з Google Calendar. Рекомендую всім!",
                rating=5,
                language="uk",
                country="UA",
                author_hint="Ірина",
                created_at=now - timedelta(hours=8),
                fetched_at=now - timedelta(minutes=20),
                content_hash="hash_007"
            ),

            # Нейтральний відгук - Google Play (змішані почуття)
            ReviewFromDB(
                id="review_008",
                source=ReviewSource.googleplay,
                backlink="https://play.google.com/review/008",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Є плюси і мінуси",
                text="Функціонал хороший, але ціна підписки завищена. За такі гроші можна було б додати більше можливостей. Ще іноді реклама показується навіть в преміум версії.",
                rating=3,
                language="uk",
                country="UA",
                author_hint="Петро_88",
                created_at=now - timedelta(hours=18),
                fetched_at=now - timedelta(hours=1),
                content_hash="hash_008"
            ),

            # Англомовний позитивний відгук
            ReviewFromDB(
                id="review_009",
                source=ReviewSource.appstore,
                backlink="https://apps.apple.com/review/009",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Great pdmodule!",
                text="Love the new design and features. Very intuitive and user-friendly. Customer support is also very responsive and helpful. Keep up the good work!",
                rating=5,
                language="en",
                country="US",
                author_hint="JohnD",
                created_at=now - timedelta(hours=4),
                fetched_at=now - timedelta(minutes=10),
                content_hash="hash_009"
            ),

            # Англомовний негативний відгук (баги)
            ReviewFromDB(
                id="review_010",
                source=ReviewSource.googleplay,
                backlink="https://play.google.com/review/010",
                brand="TestBrand",
                is_processed=False,
                app_identifier="com.testbrand.pdmodule",
                title="Crashes all the time",
                text="App keeps crashing every time I try to save my work. Lost important data twice already. This is unacceptable. Please fix these bugs ASAP!",
                rating=1,
                language="en",
                country="US",
                author_hint="Sarah_92",
                created_at=now - timedelta(hours=10),
                fetched_at=now - timedelta(minutes=25),
                content_hash="hash_010"
            )
        ]

        # Фільтруємо вже оброблені
        unprocessed = [
            review for review in mock_reviews
            if review.id not in self.processed_ids
        ]
        
        # Фільтруємо по бренду якщо вказано
        if brand:
            unprocessed = [review for review in unprocessed if review.brand == brand]
            logger.info(f"Filtered by brand '{brand}': {len(unprocessed)} reviews")

        logger.info(f"Returning {len(unprocessed)} unprocessed mock reviews")
        return unprocessed

    async def mark_as_processed(self, source: str, review_id: str) -> bool:
        """
        Позначає відгук як оброблений (додає в set)

        Args:
            source: Джерело відгуку
            review_id: ID відгуку

        Returns:
            bool: True якщо успішно
        """
        # Зберігаємо просто review_id, бо у mock даних id унікальні
        self.processed_ids.add(review_id)
        logger.info(f"Mock: Marked review {source}#{review_id} as processed")
        return True

    def reset_processed(self):
        """
        Скидає список оброблених відгуків (для тестування)
        """
        self.processed_ids.clear()
        logger.info("Mock: Reset all processed reviews")

    def get_stats(self) -> dict:
        """
        Повертає статистику mock сервісу
        """
        return {
            "total_mock_reviews": 10,
            "processed_count": len(self.processed_ids),
            "processed_ids": list(self.processed_ids)
        }