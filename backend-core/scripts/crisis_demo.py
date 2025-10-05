"""
Live Crisis Simulator - для демонстрації на хакатоні
Симулює сплеск негативних відгуків в реальному часі
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests
from datetime import datetime
import random

API_BASE = "http://localhost:8000"

CRISIS_COMMENTS = [
    "Додаток Zara крашиться при спробі оплатити! Це жах!",
    "Не можу завершити покупку, програма вилітає постійно",
    "Payment failure! Зараз уже 5 разів намагався оплатити",
    "Це скам??? Гроші списали але замовлення не пройшло!!!",
    "Додаток взагалі не працює, оплата зависає",
    "Broken app! Можна повернути гроші?",
    "НЕ ПРАЦЮЄ оплата через додаток вже 2 години!!!",
    "Краш при checkout, втратив 30 хвилин часу",
    "Zara додаток - повне лайно, не можу нічого купити",
    "REFUND! Система оплати не працює взагалі!",
]


def trigger_crisis():
    """Генерує сплеск негативних коментарів"""
    print("🚨 LIVE CRISIS SIMULATION")
    print("=" * 60)
    print("Сценарій: 15 користувачів написали про проблему з оплатою")
    print("Дивіться як BrandPulse реагує в реальному часі...\n")
    
    print("⏱️  Генеруємо сплеск негативних відгуків...")
    
    for i in range(15):
        comment = random.choice(CRISIS_COMMENTS)
        platform = random.choice(["app_store", "google_play", "trustpilot", "reddit"])
        
        data = {
            "body": comment,
            "timestamp": datetime.now().isoformat(),
            "rating": random.uniform(1.0, 2.0),
            "backlink": f"https://{platform}/crisis_comment_{i}",
            "platform": platform,
            "sentiment": "negative",
            "llm_description": "Користувач скаржиться на краш додатку при оплаті",
            "category": "payment_crash"
        }
        
        try:
            response = requests.post(f"{API_BASE}/api/comments", json=data)
            if response.status_code == 200:
                print(f"   ✓ [{i+1}/15] Додано коментар з {platform}")
            else:
                print(f"   ✗ [{i+1}/15] Помилка: {response.status_code}")
        except Exception as e:
            print(f"   ✗ [{i+1}/15] Помилка з'єднання: {e}")
        
        time.sleep(0.3)  # Невелика затримка для ефекту
    
    print("\n🔍 Перевіряємо детекцію кризи...")
    time.sleep(1)
    
    try:
        crisis_response = requests.get(f"{API_BASE}/api/crisis/check")
        crisis_data = crisis_response.json()
        
        if crisis_data.get("crisis_detected"):
            alert = crisis_data["alert"]
            print("\n🚨 CRISIS DETECTED!")
            print("=" * 60)
            print(f"Crisis Level: {alert['crisis_level'].upper()}")
            print(f"Platform: {alert.get('platform', 'Multiple')}")
            print(f"Affected Count: {alert['affected_count']}")
            print(f"Critical Keywords: {', '.join(alert['critical_keywords'])}")
            print(f"\nDescription: {alert['description']}")
            print("\n📋 Recommendations:")
            for i, rec in enumerate(alert['recommendations'], 1):
                print(f"   {i}. {rec}")
        else:
            print("\n✅ Кризу не виявлено (можливо baseline ще не розрахований)")
    
    except Exception as e:
        print(f"\n❌ Помилка при перевірці кризи: {e}")
    
    print("\n📊 Отримуємо статистику...")
    time.sleep(0.5)
    
    try:
        stats_response = requests.get(f"{API_BASE}/api/statistics")
        stats = stats_response.json()
        
        print("\n📈 STATISTICS")
        print("=" * 60)
        print(f"Total Mentions: {stats['total_mentions']}")
        print(f"Average Rating: {stats.get('average_rating', 'N/A')}")
        print(f"\nSentiment Distribution:")
        for sentiment, count in stats['sentiment_distribution'].items():
            percentage = (count / stats['total_mentions'] * 100) if stats['total_mentions'] > 0 else 0
            print(f"   {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        score = stats['reputation_score']
        print(f"\nReputation Score: {score['overall_score']}/100")
        print(f"Trend: {score['trend'].upper()}")
        print(f"Risk Level: {score['risk_level'].upper()}")
        
        if score.get('platform_scores'):
            print("\nPlatform Scores:")
            for platform, pscore in score['platform_scores'].items():
                print(f"   {platform}: {pscore}/100")
    
    except Exception as e:
        print(f"\n❌ Помилка при отриманні статистики: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Simulation Complete!")
    print("\n💡 Наступні кроки:")
    print("   1. Згенеруйте відповіді на коментарі: POST /api/generate-response")
    print("   2. Запитайте AI про проблему: POST /api/chat")
    print("   3. Перегляньте дашборд статистики")


def show_ai_response_demo():
    """Демонструє генерацію відповідей AI"""
    print("\n🤖 AI RESPONSE CO-PILOT DEMO")
    print("=" * 60)
    
    # Отримуємо останній коментар
    try:
        search_response = requests.get(f"{API_BASE}/api/search/comments?query=payment&limit=1")
        comments = search_response.json()
        
        if comments.get('results') and len(comments['results']) > 0:
            comment = comments['results'][0]
            comment_id = comment['id']
            
            print(f"Коментар: \"{comment['text'][:100]}...\"")
            print(f"Platform: {comment['platform']}, Sentiment: {comment['sentiment']}\n")
            
            print("Генеруємо відповіді у різних стилях...")
            
            response = requests.post(f"{API_BASE}/api/generate-response", json={
                "comment_id": comment_id,
                "tones": ["official", "friendly", "tech_support"],
                "tone_adjustment": 0.6
            })
            
            if response.status_code == 200:
                drafts = response.json()
                
                for draft in drafts:
                    print(f"\n{'='*60}")
                    print(f"TONE: {draft['tone'].upper()}")
                    print(f"{'='*60}")
                    print(f"\n{draft['text']}\n")
                    
                    if draft.get('action_items'):
                        print("Action Items:")
                        for action in draft['action_items']:
                            print(f"   • {action}")
                    
                    if draft.get('suggested_links'):
                        print("\nSuggested Links:")
                        for link in draft['suggested_links']:
                            print(f"   • {link}")
            else:
                print(f"Помилка при генерації відповідей: {response.status_code}")
        else:
            print("Коментарі не знайдено")
    
    except Exception as e:
        print(f"Помилка: {e}")


def chat_demo():
    """Демонструє роботу чату"""
    print("\n💬 SMART CHAT DEMO")
    print("=" * 60)
    
    questions = [
        "Які найпоширеніші проблеми з Zara?",
        "Скільки негативних відгуків про оплату?",
        "Які статті видає пошук про Zara?"
    ]
    
    for question in questions:
        print(f"\n❓ {question}")
        print("-" * 60)
        
        try:
            response = requests.post(f"{API_BASE}/api/chat", json={
                "message": question
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n{data['answer']}\n")
                print(f"Sources: {data['sources']['comments_count']} comments, {data['sources']['knowledge_docs_count']} docs")
            else:
                print(f"Помилка: {response.status_code}")
        
        except Exception as e:
            print(f"Помилка: {e}")
        
        time.sleep(1)


if __name__ == "__main__":
    print("\n" + "🎯" * 30)
    print("BRANDPULSE - LIVE DEMO")
    print("🎯" * 30 + "\n")
    
    # Перевірка доступності API
    try:
        health = requests.get(f"{API_BASE}/")
        print(f"✅ API доступний: {health.json()}\n")
    except:
        print("❌ API не доступний! Запустіть сервер: python app/main.py")
        sys.exit(1)
    
    # Запуск симуляції
    trigger_crisis()
    
    # Демо відповідей
    time.sleep(2)
    show_ai_response_demo()
    
    # Демо чату
    time.sleep(2)
    chat_demo()
    
    print("\n" + "=" * 60)
    print("🎉 DEMO ЗАВЕРШЕНО!")
    print("=" * 60)
