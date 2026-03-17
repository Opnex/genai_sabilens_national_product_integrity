"""Configuration module"""
from typing import Any, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # App
    APP_NAME: str = "SabiLens"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/sabilens"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AUTH_AUTO_ACTIVATE: bool = True

    # AI Service Endpoints
    AI_VISUAL_ENDPOINT: str = "http://localhost:8001/visual"
    AI_OCR_ENDPOINT: str = "http://localhost:8002/ocr"
    AI_REGULATORY_ENDPOINT: str = "http://localhost:8003/regulatory"
    AI_FUSION_ENDPOINT: str = "http://localhost:8004/fusion"

    # File Storage
    CLOUDINARY_URL: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, value: Any) -> Any:
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"release", "prod", "production"}:
                return False
            if lowered in {"dev", "development", "debug"}:
                return True
        return value

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
