import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Crisis detection parameters (renamed to Alert Detection)
    ALERT_CHECK_DAYS: int = 2  # Перевірка за останні 2 дні
    ALERT_NEGATIVE_INCREASE_THRESHOLD: float = 1.5  # 1.5x збільшення негативу
    CRISIS_SPIKE_MULTIPLIER: float = 3.0  # 3x від базового рівня
    CRISIS_NEGATIVE_THRESHOLD: float = 0.7  # 70% негативу
    CRISIS_CRITICAL_KEYWORDS: list = [
        "crash", "не працює", "не работает", "scam", "шахрайство",
        "broken", "refund", "повернути гроші", "lawsuit", "позов"
    ]
    
    # Baseline calculation
    BASELINE_DAYS: int = 30
    
    # Collections
    COMMENTS_COLLECTION: str = "comments"
    DOCUMENTS_COLLECTION: str = "documents"
    SERP_COLLECTION: str = "serp_results"


settings = Settings()
