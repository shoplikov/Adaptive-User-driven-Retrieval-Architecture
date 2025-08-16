"""Configuration settings for analytics service"""
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings using environment variables"""

    # Database configuration - Fixed the space in the connection string
    ANALYTICS_DATABASE_URL: str = os.getenv(
        "ANALYTICS_DATABASE_URL", 
        "postgresql://postgres:master@localhost:5432/analytics"  # Removed space before @
    )

    # Application configuration
    APP_NAME: str = "Analytics Service"
    APP_VERSION: str = "1.0.0"

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        """Pydantic settings configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create a singleton instance of settings
settings = Settings()