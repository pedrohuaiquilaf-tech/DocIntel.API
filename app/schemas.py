from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatCreateSessionRequest(BaseModel):
    document_id: UUID


class ChatCreateMessageRequest(BaseModel):
    content: str = Field(min_length=1)


class ChatSessionResponse(BaseModel):
    id: UUID
    document_id: UUID
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


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
