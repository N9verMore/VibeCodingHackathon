"""
Простий тест для перевірки основних функцій BrandPulse
Запустити: python scripts/test_basic.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.database import db_manager
from app.analytics import analytics_service


def test_database():
    """Тест роботи з ChromaDB"""
    print("🧪 Тест 1: ChromaDB")
    print("-" * 60)
    
    # Додаємо тестовий коментар
    test_comment = {
        "body": "Тестовий коментар",
        "timestamp": datetime.now(),
        "rating": 5.0,
        "platform": "app_store",
        "sentiment": "positive",
        "llm_description": "Тест",
        "category": "test"
    }
    
    comment_id = db_manager.add_comment(test_comment)
    print(f"✅ Коментар додано: {comment_id}")
    
    # Додаємо тестовий документ
    doc_id = db_manager.add_document(
        title="Тестовий документ",
        content="Це тестовий контент",
        doc_type="test"
    )
    print(f"✅ Документ додано: {doc_id}")
    
    # Перевіряємо пошук
    search_results = db_manager.search_comments("тест", n_results=5)
    print(f"✅ Пошук працює: знайдено {len(search_results.get('ids', [[]])[0])} результатів")
    
    print()


def test_analytics():
    """Тест аналітики"""
    print("🧪 Тест 2: Analytics Service")
    print("-" * 60)
    
    # Отримуємо статистику
    stats = analytics_service.get_statistics()
    print(f"✅ Статистика отримана:")
    print(f"   - Всього згадувань: {stats['total_mentions']}")
    print(f"   - Позитивних: {stats['sentiment_distribution'].get('positive', 0)}")
    print(f"   - Негативних: {stats['sentiment_distribution'].get('negative', 0)}")
    
    # Розраховуємо reputation score
    score = analytics_service.calculate_reputation_score()
    print(f"✅ Reputation Score: {score['overall_score']}/100")
    print(f"   - Тренд: {score['trend']}")
    print(f"   - Рівень ризику: {score['risk_level']}")
    
    # Перевіряємо детекцію кризи
    crisis = analytics_service.detect_crisis()
    if crisis:
        print(f"⚠️  Криза виявлена: {crisis.crisis_level}")
    else:
        print(f"✅ Криз не виявлено")
    
    print()


def test_data_integrity():
    """Тест цілісності даних"""
    print("🧪 Тест 3: Data Integrity")
    print("-" * 60)
    
    all_comments = db_manager.get_all_comments()
    
    if not all_comments["metadatas"]:
        print("⚠️  База даних порожня. Запустіть: python scripts/generate_test_data.py")
        return
    
    # Перевірка структури даних
    required_fields = ["platform", "sentiment", "timestamp"]
    
    valid_count = 0
    for metadata in all_comments["metadatas"]:
        if all(field in metadata for field in required_fields):
            valid_count += 1
    
    total = len(all_comments["metadatas"])
    print(f"✅ Валідних записів: {valid_count}/{total}")
    
    # Перевірка платформ
    platforms = set(m.get("platform") for m in all_comments["metadatas"])
    print(f"✅ Платформи: {', '.join(platforms)}")
    
    # Перевірка sentiment
    sentiments = {}
    for m in all_comments["metadatas"]:
        sent = m.get("sentiment", "unknown")
        sentiments[sent] = sentiments.get(sent, 0) + 1
    
    print(f"✅ Розподіл sentiment:")
    for sent, count in sentiments.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   - {sent}: {count} ({percentage:.1f}%)")
    
    print()


def main():
    print("\n" + "=" * 60)
    print("BRANDPULSE - BASIC TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_database()
        test_analytics()
        test_data_integrity()
        
        print("=" * 60)
        print("✅ Всі тести пройдені успішно!")
        print("=" * 60)
        print("\n💡 Наступні кроки:")
        print("   1. Запустіть сервер: python app/main.py")
        print("   2. Відкрийте: http://localhost:8000/docs")
        print("   3. Запустіть demo: python scripts/crisis_demo.py")
        
    except Exception as e:
        print(f"\n❌ Помилка під час тестування: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
