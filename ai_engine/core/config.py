"""Application configuration management."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    APP_NAME: str = "AegisX AI Engine"
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    LOG_LEVEL: str = Field(default="INFO")

    DATABASE_PATH: str = Field(default="../data/aegisx.db")

    ALLOWED_ORIGINS: List[str] = Field(default=["*"])

    PROMPTS_DIR: str = Field(default="../prompts")


settings = Settings()
