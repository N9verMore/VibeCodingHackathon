"""
Тест ендпоінту /api/reviews/external
"""
import requests
import json

API_URL = "http://localhost:8000"

# Тестові дані у вашому форматі
test_data = {
    "reviews": [
        {
            "id": "review_001",
            "source": "appstore",
            "backlink": "https://apps.apple.com/review/001",
            "text": "Користуюся вже місяць, все працює відмінно. Інтерфейс зручний, швидко завантажується. Особливо подобається функція автоматичного збереження.",
            "rating": 5,
            "created_at": "2025-10-02T11:08:15.919438",
            "sentiment": "позитивний",
            "description": "Користувач хвалить додаток за зручний інтерфейс, швидкість завантаження та функцію автоматичного збереження.",
            "categories": ["інтерфейс", "функціональність"],
            "severity": "low",
            "is_processed": True
        },
        {
            "id": "review_002",
            "source": "googleplay",
            "backlink": "https://play.google.com/review/002",
            "text": "Намагаюся оплатити преміум підписку, але постійно вилітає помилка. Підтримка не відповідає вже 3 дні. Дуже розчарований.",
            "rating": 1,
            "created_at": "2025-10-03T11:08:15.919438",
            "sentiment": "негативний",
            "description": "Користувач не може оплатити преміум підписку через постійні помилки і не отримує відповіді від підтримки.",
            "categories": ["оплата"],
            "severity": "critical",
            "is_processed": True
        },
        {
            "id": "review_003",
            "source": "trustpilot",
            "backlink": "https://trustpilot.com/review/003",
            "text": "Загалом додаток робочий. Є деякі баги, наприклад іноді не синхронізуються дані. Але в цілому функціонал задовольняє базові потреби.",
            "rating": 3,
            "created_at": "2025-10-03T23:08:15.919438",
            "sentiment": "нейтральний",
            "description": "Користувач вважає додаток робочим, але зазначає наявність багів, зокрема проблеми з синхронізацією даних.",
            "categories": ["функціональність"],
            "severity": "medium",
            "is_processed": True
        }
    ],
    "count": 3
}


def test_external_reviews():
    """Тест ендпоінту /api/reviews/external"""
    print("🧪 Тестування /api/reviews/external")
    print("=" * 60)
    
    # 1. Перевірка health check
    print("\n1️⃣ Health check...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"   ✓ API доступний: {response.json()}")
    except Exception as e:
        print(f"   ✗ API недоступний: {e}")
        return
    
    # 2. Відправка тестових даних
    print("\n2️⃣ Відправка тестових відгуків...")
    print(f"   Відгуків: {len(test_data['reviews'])}")
    print(f"   Формат даних:")
    print(f"   - source: {test_data['reviews'][0]['source']}")
    print(f"   - category (type): {type(test_data['reviews'][0]['category'])}")
    print(f"   - category (value): {test_data['reviews'][0]['category']}")
    print(f"   - severity: {test_data['reviews'][0]['severity']}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/reviews/external",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Успіх!")
            print(f"   Додано: {result['added_count']} відгуків")
            print(f"   IDs: {result['comment_ids'][:3]}...")
            return result
        else:
            print(f"   ✗ Помилка!")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_statistics():
    """Перевірка статистики після додавання"""
    print("\n3️⃣ Перевірка статистики...")
    
    try:
        response = requests.get(f"{API_URL}/api/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ Статистика отримана")
            print(f"   Total mentions: {stats['total_mentions']}")
            print(f"   Sentiment: {stats['sentiment_distribution']}")
            
            if 'severity_distribution' in stats:
                print(f"   Severity: {stats['severity_distribution']}")
            else:
                print(f"   ⚠️  severity_distribution відсутній!")
            
            print(f"   Top categories: {stats['top_categories'][:3]}")
        else:
            print(f"   ✗ Помилка: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")


def test_search():
    """Тест пошуку"""
    print("\n4️⃣ Тест пошуку...")
    
    try:
        response = requests.get(f"{API_URL}/api/search/comments?query=оплата&limit=5")
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✓ Знайдено: {results['total']} результатів")
            
            if results['results']:
                first = results['results'][0]
                print(f"   Перший результат:")
                print(f"   - Text: {first['text'][:60]}...")
                print(f"   - Category: {first.get('category')}")
                print(f"   - Severity: {first.get('severity')}")
        else:
            print(f"   ✗ Помилка: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")


if __name__ == "__main__":
    print("\n" + "🎯" * 30)
    print("ТЕСТ ЕНДПОІНТУ /api/reviews/external")
    print("🎯" * 30 + "\n")
    
    result = test_external_reviews()
    
    if result:
        test_statistics()
        test_search()
        
        print("\n" + "=" * 60)
        print("✅ ТЕСТИ ЗАВЕРШЕНІ")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ ТЕСТИ НЕ ПРОЙДЕНІ - перевірте логи сервера")
        print("=" * 60)
