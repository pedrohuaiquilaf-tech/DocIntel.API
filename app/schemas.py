from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentPreview(BaseModel):
    id: UUID
    filename: str
    page_count: int
    preview: str
    uploaded_at: datetime

    model_config = {
        "from_attributes": True,
    }


class HealthResponse(BaseModel):
    status: str = Field("ok")
