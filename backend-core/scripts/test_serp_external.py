"""
Тестування додавання Google SERP результатів через /api/reviews/external
"""
import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

# Тестові SERP результати про Zara
serp_results = [
    {
        "id": "serp_001",
        "source": "google_search",
        "backlink": "https://www.bbc.com/news/zara-fast-fashion-criticism",
        "text": "Zara Faces Criticism Over Fast Fashion Practices\n\nZara, the Spanish fashion giant, is facing renewed criticism over its fast fashion model. Environmental groups claim the company's rapid production cycles contribute to textile waste and pollution.",
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "sentiment": "негативний",
        "description": "Негативна стаття про практики швидкої моди Zara та їх вплив на екологію",
        "categories": ["екологія", "виробництво", "репутація"],
        "severity": "high"
    },
    {
        "id": "serp_002",
        "source": "google_search",
        "backlink": "https://www.forbes.com/zara-sustainability-initiative",
        "text": "Zara Announces Major Sustainability Initiative\n\nInditex's flagship brand Zara has unveiled plans to make all its clothing from sustainable materials by 2025. The initiative includes partnerships with recycling companies and a new take-back program.",
        "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
        "sentiment": "позитивний",
        "description": "Позитивна новина про екологічні ініціативи Zara та плани на майбутнє",
        "categories": ["екологія", "інновації", "корпоративна відповідальність"],
        "severity": "low"
    },
    {
        "id": "serp_003",
        "source": "google_search",
        "backlink": "https://www.theguardian.com/zara-workers-rights",
        "text": "Zara Supplier Factories Under Investigation\n\nSeveral factories supplying Zara have been placed under investigation following reports of poor working conditions. Labor rights organizations are calling for immediate action and transparency.",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "sentiment": "негативний",
        "description": "Скандал з правами працівників на фабриках-постачальниках Zara",
        "categories": ["права працівників", "етика", "виробництво"],
        "severity": "critical"
    },
    {
        "id": "serp_004",
        "source": "google_search",
        "backlink": "https://www.vogue.com/zara-new-collection-2025",
        "text": "Zara's Spring 2025 Collection Wins Fashion Critics' Praise\n\nZara's latest spring collection has been met with enthusiasm from fashion critics. The collection features minimalist designs with sustainable fabrics, marking a shift in the brand's aesthetic.",
        "created_at": (datetime.now() - timedelta(hours=12)).isoformat(),
        "sentiment": "позитивний",
        "description": "Позитивна рецензія нової колекції Zara від модних критиків",
        "categories": ["дизайн", "мода", "колекції"],
        "severity": "low"
    },
    {
        "id": "serp_005",
        "source": "google_search",
        "backlink": "https://www.reuters.com/zara-sales-decline",
        "text": "Zara Reports Sales Decline in European Markets\n\nZara parent company Inditex reported a 3.5% decline in European sales for Q3. Analysts attribute this to increased competition from online-only retailers and changing consumer preferences.",
        "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
        "sentiment": "негативний",
        "description": "Зниження продажів Zara в Європі через конкуренцію з онлайн-ритейлерами",
        "categories": ["продажі", "фінанси", "конкуренція"],
        "severity": "medium"
    },
    {
        "id": "serp_006",
        "source": "google_search",
        "backlink": "https://techcrunch.com/zara-ar-app-launch",
        "text": "Zara Launches Augmented Reality Shopping App\n\nZara has introduced a new AR-powered mobile app that allows customers to virtually try on clothes before purchasing. Early reviews praise the technology as 'game-changing' for online fashion retail.",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
        "sentiment": "позитивний",
        "description": "Інноваційний AR додаток від Zara для віртуальної примірки одягу",
        "categories": ["технології", "інновації", "додаток"],
        "severity": "low"
    },
    {
        "id": "serp_007",
        "source": "google_search",
        "backlink": "https://www.businessinsider.com/zara-data-breach-2025",
        "text": "Zara Confirms Customer Data Breach Affecting Millions\n\nZara has confirmed a data breach that exposed personal information of approximately 2.3 million customers. The company is offering free credit monitoring services to affected customers.",
        "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
        "sentiment": "негативний",
        "description": "Серйозна витока даних клієнтів Zara, постраждали мільйони користувачів",
        "categories": ["безпека", "дані", "приватність"],
        "severity": "critical"
    },
    {
        "id": "serp_008",
        "source": "google_search",
        "backlink": "https://www.elle.com/zara-celebrity-collaboration",
        "text": "Zara Announces Collaboration with Rising Designer\n\nZara has announced a limited-edition collaboration with award-winning designer Sofia Martinez. The collection will feature 50 exclusive pieces combining Martinez's signature style with Zara's accessibility.",
        "created_at": (datetime.now() - timedelta(days=4)).isoformat(),
        "sentiment": "позитивний",
        "description": "Цікава колаборація Zara з відомим дизайнером",
        "categories": ["дизайн", "колаборації", "маркетинг"],
        "severity": "low"
    }
]


def add_serp_results():
    """Додати SERP результати"""
    print(f"📰 Додаємо {len(serp_results)} SERP результатів через /api/reviews/external...")
    
    # Відправляємо в тому ж форматі що й reviews
    batch = {
        "reviews": serp_results,
        "count": len(serp_results)
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/reviews/external",
            json=batch,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Успішно додано: {result['added_count']} SERP результатів")
        print(f"📊 IDs: {result['comment_ids'][:3]}...")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Помилка: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None


def test_filter_serp():
    """Тестування фільтрації SERP результатів"""
    print("\n🔍 Тестуємо фільтрацію SERP результатів...")
    
    # 1. Всі SERP результати
    print("\n1️⃣ Всі результати з google_serp:")
    response = requests.post(
        f"{API_URL}/api/reviews/filter",
        json={
            "platforms": ["google_serp"],
            "limit": 20
        }
    )
    
    if response.ok:
        data = response.json()
        print(f"   Знайдено: {data['pagination']['filtered_count']}")
        for item in data['data'][:3]:
            print(f"   - [{item['severity']}] {item['text'][:60]}...")
    
    # 2. Критичні новини
    print("\n2️⃣ Критичні SERP результати:")
    response = requests.post(
        f"{API_URL}/api/reviews/filter",
        json={
            "platforms": ["google_serp"],
            "severity": ["critical"],
            "limit": 10
        }
    )
    
    if response.ok:
        data = response.json()
        print(f"   Знайдено: {data['pagination']['filtered_count']}")
        for item in data['data']:
            print(f"   - {item['text'][:80]}...")
            print(f"     Категорії: {', '.join(item['category'])}")
    
    # 3. Негативні новини за останні 3 дні
    print("\n3️⃣ Негативні SERP за останні 3 дні:")
    three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
    
    response = requests.post(
        f"{API_URL}/api/reviews/filter",
        json={
            "platforms": ["google_serp"],
            "sentiment": ["negative"],
            "date_from": three_days_ago,
            "sort_by": "timestamp",
            "sort_order": "desc"
        }
    )
    
    if response.ok:
        data = response.json()
        print(f"   Знайдено: {data['pagination']['filtered_count']}")
        for item in data['data'][:5]:
            print(f"   - [{item['severity']}] {item['text'][:70]}...")
    
    # 4. Комбінований запит: reviews + SERP
    print("\n4️⃣ Всі негативні (reviews + SERP):")
    response = requests.post(
        f"{API_URL}/api/reviews/filter",
        json={
            "sentiment": ["negative"],
            "severity": ["high", "critical"],
            "limit": 30
        }
    )
    
    if response.ok:
        data = response.json()
        print(f"   Знайдено: {data['pagination']['filtered_count']}")
        
        # Групуємо по платформах
        by_platform = {}
        for item in data['data']:
            platform = item['platform']
            by_platform[platform] = by_platform.get(platform, 0) + 1
        
        print(f"   Розподіл по платформах:")
        for platform, count in by_platform.items():
            print(f"   - {platform}: {count}")


def test_statistics_with_serp():
    """Перевірка статистики з SERP"""
    print("\n📊 Статистика з SERP результатами...")
    
    response = requests.get(f"{API_URL}/api/statistics")
    
    if response.ok:
        stats = response.json()
        print(f"Всього згадувань: {stats['total_mentions']}")
        print(f"\nРозподіл по платформах:")
        for platform, count in stats['platform_distribution'].items():
            print(f"  - {platform}: {count}")
        
        print(f"\nSeverity distribution:")
        if stats.get('severity_distribution'):
            for severity, count in stats['severity_distribution'].items():
                print(f"  - {severity}: {count}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ТЕСТУВАННЯ SERP ЧЕРЕЗ /api/reviews/external")
    print("=" * 60)
    
    # Додаємо SERP результати
    result = add_serp_results()
    
    if result:
        # Тестуємо фільтрацію
        test_filter_serp()
        
        # Перевіряємо статистику
        test_statistics_with_serp()
    
    print("\n" + "=" * 60)
    print("✅ Тестування завершено!")
    print("=" * 60)
