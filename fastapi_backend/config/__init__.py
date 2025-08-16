"""
Configuration module for FastAPI backend.
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Database configuration
    POSTGRES_USER: str = os.getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD", "master")
    POSTGRES_DB: str = os.getenv("DB_NAME", "aura_chatbot")
    POSTGRES_HOST: str = os.getenv("DB_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("DB_PORT", "5432"))

    # LMStudio configuration
    LMSTUDIO_ENDPOINT: str = os.getenv("LLM_API_BASE", "http://localhost:1234/v1/chat/completions")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "hermes-3-llama-3.2-3b")
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))

    # RAG Configuration
    RAG_DOCS_PATH: str = os.getenv("RAG_DOCS_PATH", os.path.join("RAG", "documents.json"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
    RAG_USE_RERANKER: bool = os.getenv("RAG_USE_RERANKER", "true").lower() == "true"

    # Feedback
    FEEDBACK_STRATEGY_PATH: str = os.getenv("FEEDBACK_STRATEGY_PATH", os.path.join("wildfeedback", "data", "strategies.json"))
    FEEDBACK_CLASSIFIER_PATH: str = os.getenv("FEEDBACK_CLASSIFIER_PATH", os.path.join("wildfeedback", "praise_classifier.pkl"))

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

# Create a singleton instance of settings
settings = Settings()

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"