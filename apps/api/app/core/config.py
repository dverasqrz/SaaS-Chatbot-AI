from __future__ import annotations

import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _settings_env_file() -> str | None:
    # Em produção (Docker) usa só variáveis do ambiente; evita que um .env copiado
    # para a imagem sobrescreva DATABASE_URL com localhost.
    if os.getenv("APP_ENV", "").lower() == "production":
        return None
    return ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_settings_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SaaS Chatbot AI API"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str = Field(
        default="postgresql+psycopg://saas_chat:saas_chat@db:5432/saas_chat"
    )
    redis_url: str = "redis://redis:6379/0"

    jwt_secret_key: SecretStr = Field(default=SecretStr("change-this-in-production"))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    cors_origins: str = "http://localhost:3000"


settings = Settings()
