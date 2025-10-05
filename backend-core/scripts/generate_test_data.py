"""
Генератор тестових даних для BrandPulse про бренд Zara
ОНОВЛЕНО: додано підтримку масиву категорій та severity
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random
from app.database import db_manager
from app.models import Platform, Sentiment

# Тестові дані про Zara (текст, категорії[], рейтинг, severity)
ZARA_COMMENTS = {
    "positive": [
        ("Чудова якість одягу від Zara! Завжди знаходжу щось стильне", ["якість", "продукт"], 5.0, "low"),
        ("Нова колекція Zara просто вогонь 🔥 Купила вже три речі", ["продукт", "дизайн"], 5.0, "low"),
        ("Дуже швидка доставка, замовлення прийшло за 2 дні!", ["доставка"], 5.0, "low"),
        ("Zara має найкращі базові речі за адекватну ціну", ["ціна", "якість"], 4.5, "low"),
        ("Обожнюю Zara! Їхні джинси ідеально сидять", ["продукт", "розмір"], 5.0, "low"),
        ("Відмінне обслуговування в магазині, консультанти дуже допомогли", ["підтримка", "сервіс"], 4.5, "low"),
        ("Повернення товару пройшло без проблем, дякую Zara", ["повернення"], 4.0, "low"),
        ("Приємні ціни під час розпродажу, взяла пальто зі знижкою 50%", ["ціна", "акції"], 5.0, "low"),
        ("Додаток Zara дуже зручний, легко шукати товари", ["додаток", "інтерфейс"], 4.0, "low"),
        ("Якість тканин вражає за таку ціну, рекомендую!", ["якість", "ціна"], 5.0, "low"),
    ],
    "neutral": [
        ("Zara непогана, але якість іноді буває різною", ["якість"], 3.0, "medium"),
        ("Замовила сукню з Zara, розмір підійшов", ["розмір"], 3.5, "low"),
        ("В магазині Zara великий асортимент, але не завжди мій розмір", ["асортимент", "розмір"], 3.0, "medium"),
        ("Ціни в Zara середні, є й дешевше варіанти", ["ціна"], 3.0, "low"),
        ("Доставка зайняла тиждень, очікувала швидше", ["доставка"], 3.0, "medium"),
        ("Zara нормальний бренд для базового гардеробу", ["загальне"], 3.5, "low"),
        ("Якість як і скрізь в масмаркеті, нічого особливого", ["якість"], 3.0, "low"),
        ("Додаток Zara працює, але хотілося б більше фільтрів", ["додаток", "функціональність"], 3.0, "medium"),
    ],
    "negative": [
        ("Додаток Zara постійно вилітає при оплаті! Вже втретє намагаюся", ["оплата", "краш", "додаток"], 1.0, "critical"),
        ("Замовлення не прийшло вчасно, підтримка не відповідає", ["доставка", "підтримка"], 1.5, "high"),
        ("Якість речей з Zara сильно впала останнім часом", ["якість"], 2.0, "medium"),
        ("Не можу оплатити замовлення в додатку Zara, пише помилку", ["оплата", "додаток"], 1.0, "critical"),
        ("Зробила замовлення, але воно загубилося. Гроші списали!", ["замовлення", "оплата"], 1.0, "critical"),
        ("Розміри в Zara взагалі не відповідають дійсності", ["розмір"], 2.0, "medium"),
        ("Підтримка Zara жахлива, чекаю відповіді вже 3 дні", ["підтримка"], 1.5, "high"),
        ("Повернути товар в Zara неможливо, відмовили без причини", ["повернення", "підтримка"], 1.0, "high"),
        ("Додаток Zara лагає і не зберігає мої дані", ["додаток", "баги"], 2.0, "high"),
        ("Оплата не проходить через додаток вже тиждень!", ["оплата", "додаток"], 1.0, "critical"),
        ("СКАМ! Гроші списали, а товар не відправили", ["шахрайство", "оплата"], 1.0, "critical"),
        ("Додаток крашиться кожні 5 хвилин, неможливо користуватись", ["краш", "додаток"], 1.0, "critical"),
    ]
}

ZARA_DOCUMENTS = [
    {
        "title": "Про бренд Zara",
        "content": """Zara - це іспанський бренд швидкої моди, що належить Inditex Group. 
        Заснований у 1975 році Амансіо Ортегою. Zara відома своїм підходом до швидкої моди, 
        випускаючи нові колекції кожні два тижні. Бренд має понад 2000 магазинів у 96 країнах світу.""",
        "doc_type": "brand_info"
    },
    {
        "title": "Політика повернення Zara",
        "content": """Zara надає 30 днів на повернення товару з моменту покупки. 
        Товар повинен бути в оригінальній упаковці з бирками. Повернення можливе як у магазині, 
        так і через кур'єра. Кошти повертаються протягом 14 днів на картку або рахунок.""",
        "doc_type": "policy"
    },
    {
        "title": "Оновлення додатку Zara - Версія 10.5",
        "content": """Нова версія додатку Zara (10.5) включає:
        - Покращену систему оплати
        - Новий інтерфейс каталогу
        - Персональні рекомендації на основі AI
        - Виправлення помилок з крашами при оплаті
        - Додано підтримку Apple Pay та Google Pay
        Дата релізу: 15 вересня 2025""",
        "doc_type": "release_notes"
    },
    {
        "title": "Контакти служби підтримки Zara",
        "content": """
        Служба підтримки Zara:
        - Email: support@zara.com
        - Телефон: 0-800-555-100 (безкоштовно по Україні)
        - Чат в додатку: доступний 24/7
        - Час роботи телефону: Пн-Нд 9:00-21:00
        - Середній час відповіді: до 24 годин
        """,
        "doc_type": "support_info"
    },
    {
        "title": "Розмірна сітка Zara",
        "content": """Розмірна сітка Zara може відрізнятися від стандартних розмірів.
        Рекомендується завжди перевіряти таблицю розмірів для конкретної моделі.
        XS (EU 34), S (EU 36), M (EU 38), L (EU 40), XL (EU 42).
        Зверніть увагу: азійські розміри можуть бути меншими на 1-2 розміри.""",
        "doc_type": "sizing_guide"
    }
]

SERP_RESULTS = [
    {
        "query": "Zara Ukraine",
        "title": "ZARA Ukraine - Інтернет-магазин одягу",
        "snippet": "Офіційний інтернет-магазин ZARA в Україні. Жіночий, чоловічий та дитячий одяг. Нові колекції онлайн.",
        "url": "https://www.zara.com/ua/",
        "position": 1
    },
    {
        "query": "Zara reviews",
        "title": "Відгуки про Zara - найбільша колекція відгуків",
        "snippet": "Реальні відгуки покупців про Zara. Оцінка 4.2 з 5. Читайте що пишуть користувачі про якість та доставку.",
        "url": "https://reviews.com.ua/zara",
        "position": 2
    },
    {
        "query": "Zara app problems",
        "title": "Користувачі скаржаться на проблеми з додатком Zara",
        "snippet": "Після останнього оновлення додаток Zara почав крашитися. Користувачі повідомляють про проблеми з оплатою.",
        "url": "https://news.tech/zara-app-issues",
        "position": 1
    },
    {
        "query": "Zara delivery Ukraine",
        "title": "Доставка Zara в Україні - умови та терміни",
        "snippet": "Безкоштовна доставка при замовленні від 1500 грн. Стандартна доставка 3-5 днів. Експрес доставка - 1-2 дні.",
        "url": "https://www.zara.com/ua/delivery",
        "position": 1
    }
]

LLM_DESCRIPTIONS = {
    "positive": [
        "Користувач висловлює задоволення якістю продукту",
        "Клієнт хвалить швидку доставку",
        "Позитивний відгук про обслуговування",
        "Користувач рекомендує бренд",
        "Задоволений співвідношенням ціни та якості"
    ],
    "neutral": [
        "Нейтральна згадка про бренд",
        "Користувач описує досвід без емоцій",
        "Звичайний відгук про покупку",
        "Нейтральний коментар про якість"
    ],
    "negative": [
        "Користувач скаржиться на краш додатку при оплаті",
        "Проблеми з доставкою замовлення",
        "Скарга на погану якість товару",
        "Проблеми з оплатою в додатку",
        "Скарга на повільну підтримку",
        "Користувач не задоволений послугою повернення"
    ]
}


def generate_test_data():
    """Генерує тестові дані про Zara"""
    print("🚀 Генерація тестових даних про Zara...")
    
    # 1. Додаємо документи про бренд
    print("\n📄 Додаємо документи про бренд...")
    for doc in ZARA_DOCUMENTS:
        doc_id = db_manager.add_document(
            title=doc["title"],
            content=doc["content"],
            doc_type=doc["doc_type"]
        )
        print(f"   ✓ Додано документ: {doc['title']} (ID: {doc_id})")
    
    # 2. Додаємо SERP результати
    print("\n🔍 Додаємо результати Google пошуку...")
    for serp in SERP_RESULTS:
        serp_data = {
            **serp,
            "timestamp": datetime.now() - timedelta(days=random.randint(0, 7))
        }
        serp_id = db_manager.add_serp_result(serp_data)
        print(f"   ✓ Додано SERP: {serp['title'][:50]}... (ID: {serp_id})")
    
    # 3. Генеруємо коментарі з різних платформ
    print("\n💬 Генеруємо коментарі/відгуки...")
    platforms = [Platform.APP_STORE, Platform.GOOGLE_PLAY, Platform.TRUSTPILOT, 
                 Platform.REDDIT, Platform.QUORA]
    
    total_comments = 0
    
    # Генеруємо коментарі за останні 30 днів
    for day_offset in range(30):
        base_date = datetime.now() - timedelta(days=day_offset)
        
        # Різна кількість коментарів по днях (імітація реального трафіку)
        if day_offset == 0:
            # Сьогодні - симулюємо кризу (багато негативу про краш)
            comments_count = 25
            sentiment_weights = [0.1, 0.1, 0.8]  # 80% негатив
        elif day_offset < 7:
            comments_count = random.randint(8, 15)
            sentiment_weights = [0.4, 0.2, 0.4]
        else:
            comments_count = random.randint(3, 8)
            sentiment_weights = [0.5, 0.3, 0.2]
        
        for _ in range(comments_count):
            # Вибираємо sentiment
            sentiment = random.choices(
                ["positive", "neutral", "negative"],
                weights=sentiment_weights
            )[0]
            
            # Вибираємо коментар (текст, категорії[], рейтинг, severity)
            comment_text, categories, rating, severity = random.choice(ZARA_COMMENTS[sentiment])
            
            # Додаємо варіативність
            timestamp = base_date - timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            platform = random.choice(platforms)
            
            # Для кризи сьогодні - більше crash коментарів
            if day_offset == 0 and sentiment == "negative":
                if random.random() < 0.7:  # 70% шанс
                    crash_comments = [
                        ("Додаток Zara постійно вилітає при оплаті! Вже втретє намагаюся", ["оплата", "краш", "додаток"], 1.0, "critical"),
                        ("Не можу оплатити замовлення в додатку Zara, пише помилку", ["оплата", "додаток"], 1.0, "critical"),
                        ("Додаток крашиться кожні 5 хвилин, неможливо користуватись", ["краш", "додаток"], 1.0, "critical"),
                        ("Оплата не проходить через додаток вже тиждень!", ["оплата", "додаток"], 1.0, "critical"),
                        ("СКАМ! Гроші списали, а товар не відправили", ["шахрайство", "оплата"], 1.0, "critical")
                    ]
                    comment_text, categories, rating, severity = random.choice(crash_comments)
            
            comment_data = {
                "body": comment_text,
                "timestamp": timestamp,
                "rating": rating,
                "backlink": f"https://{platform.value}/review/{random.randint(1000, 9999)}",
                "platform": platform.value,
                "sentiment": sentiment,
                "llm_description": random.choice(LLM_DESCRIPTIONS[sentiment]),
                "category": categories,  # Тепер це список
                "severity": severity  # Додано severity
            }
            
            comment_id = db_manager.add_comment(comment_data)
            total_comments += 1
    
    print(f"   ✓ Додано {total_comments} коментарів")
    
    # Статистика по платформах
    all_comments = db_manager.get_all_comments()
    platform_stats = {}
    sentiment_stats = {"positive": 0, "negative": 0, "neutral": 0}
    severity_stats = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    
    for metadata in all_comments["metadatas"]:
        platform = metadata.get("platform", "unknown")
        sentiment = metadata.get("sentiment", "neutral")
        severity = metadata.get("severity", "medium")
        platform_stats[platform] = platform_stats.get(platform, 0) + 1
        sentiment_stats[sentiment] += 1
        severity_stats[severity] += 1
    
    print("\n📊 Статистика згенерованих даних:")
    print(f"   Всього коментарів: {total_comments}")
    print(f"   Позитивних: {sentiment_stats['positive']}")
    print(f"   Нейтральних: {sentiment_stats['neutral']}")
    print(f"   Негативних: {sentiment_stats['negative']}")
    print("\n   По severity:")
    print(f"   Low: {severity_stats['low']}")
    print(f"   Medium: {severity_stats['medium']}")
    print(f"   High: {severity_stats['high']}")
    print(f"   Critical: {severity_stats['critical']}")
    print("\n   По платформах:")
    for platform, count in platform_stats.items():
        print(f"   - {platform}: {count}")
    
    print("\n✅ Тестові дані успішно згенеровано!")
    print("\n💡 Тепер можна:")
    print("   1. Запустити сервер: python app/main.py")
    print("   2. Перевірити статистику: GET /api/statistics")
    print("   3. Перевірити кризу: GET /api/crisis/check")
    print("   4. Запитати в чаті: POST /api/chat")


if __name__ == "__main__":
    generate_test_data()
