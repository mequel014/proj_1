# app/config.py
import os
from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI

load_dotenv()

class Settings:
    # Yandex LLM
    API_KEY: str = os.getenv("API_KEY", "")
    FOLDER_ID: str = os.getenv("FOLDER_ID", "")
    BASE_URL: str = os.getenv("BASE_URL", "https://llm.api.cloud.yandex.net/foundationModels/v1")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))

    # LangSmith (опционально)
    LANGSMITH_API: str = os.getenv("LANGSMITH_API", "")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Маппинг имён моделей
    MODEL_NAMES = {
        'lite': 'yandexgpt-lite',
        'pro': 'yandexgpt',
        'pro_32k': 'yandexgpt-32k',
    }

    def model_name(self, model_id: str) -> str:
        """
        gpt://<folder>/<model>/latest — формат для Yandex Cloud
        """
        return f"gpt://{self.FOLDER_ID}/{self.MODEL_NAMES[model_id]}/latest"

    @lru_cache()
    def create_yandex_model(self, model_id: str = "lite", temperature: Optional[float] = None) -> ChatOpenAI:
        """
        Создаёт (и кеширует) клиент YandexGPT через langchain_openai
        """
        if temperature is None:
            temperature = self.TEMPERATURE

        llm = ChatOpenAI(
            api_key=self.API_KEY,
            base_url=self.BASE_URL,
            model=self.model_name(model_id),
            temperature=temperature,
        )
        return llm


settings = Settings()

# Настройка переменных для LangSmith (если нужно)
if settings.LANGSMITH_API:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API
if settings.LANGSMITH_PROJECT:
    os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT