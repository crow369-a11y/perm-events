"""Конфигурация: все настройки читаются из .env (см. .env.example)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Timepad ---
    timepad_token: str = ""
    timepad_cities: str = "Пермь"
    timepad_limit: int = 50

    bot_token: str = ""

    telegram_api_id: int = 0
    telegram_api_hash: str = ""

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b-instruct"

    database_url: str = "sqlite:///data/db/app.db"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
