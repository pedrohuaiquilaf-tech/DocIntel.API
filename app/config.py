from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str | None = None
    openai_api_key: str | None = None
    max_upload_size_mb: int = 10
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "env_prefix": "",
    }


settings = Settings()
