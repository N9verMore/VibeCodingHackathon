from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Налаштування застосунку"""

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # Delivery
    deliver_endpoint: str = "http://localhost:8000/deliver_processed"

    # Processing
    batch_size: int = 10

    # Database Mode
    use_mock_db: bool = False  # True = використовувати mock дані, False = реальна БД
    use_mock_delivery: bool = True  # True = виводить у консоль, False = відправляє HTTP

    # DynamoDB (для teammate)
    aws_region: str = "us-east-1"
    dynamodb_table_name: str = "ReviewsTableV2"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # PostgreSQL
    postgres_url: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Отримати налаштування (з кешуванням)"""
    return Settings()