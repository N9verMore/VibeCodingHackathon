# ============================================
# FILE: main.py
# ============================================
from fastapi import FastAPI
import logging
from pdmodule.api import router
from pdmodule.config import get_settings

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Створення FastAPI pdmodule
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
