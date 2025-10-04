# ============================================
# FILE: main.py
# ============================================
from fastapi import FastAPI
import logging
import asyncio
import sys
from app.api import router
from app.config import get_settings

# Налаштування event loop для Windows (для psycopg)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Створення FastAPI app
app = FastAPI(
    title="Brand Reputation Defender - Review Processor",
    description="Сервіс обробки відгуків через OpenAI API",
    version="1.0.0"
)

# Підключення роутів
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=8000)
