from __future__ import annotations

import json

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str | None = None
    openai_api_key: str | None = None
    max_upload_size_mb: int = 10
    cors_origins: str | list[str] = Field(default="http://localhost:5173")

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "env_prefix": "",
    }

    @model_validator(mode="before")
    @classmethod
    def parse_cors_origins(cls, data):
        if isinstance(data, dict):
            value = data.get("cors_origins")
            if value is None:
                return data
            if isinstance(value, list):
                return data
            if isinstance(value, str):
                text = value.strip()
                if not text:
                    data["cors_origins"] = []
                elif text.startswith("["):
                    try:
                        parsed = json.loads(text)
                        data["cors_origins"] = parsed if isinstance(parsed, list) else [parsed]
                    except json.JSONDecodeError:
                        data["cors_origins"] = [text]
                elif "," in text:
                    data["cors_origins"] = [item.strip() for item in text.split(",") if item.strip()]
                else:
                    data["cors_origins"] = [text]
        return data

    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [self.cors_origins]


settings = Settings()
