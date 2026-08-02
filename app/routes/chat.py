from __future__ import annotations

import json
from typing import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import ChatMessage, ChatSession, Document
from app.schemas import ChatCreateSessionRequest, ChatCreateMessageRequest, ChatMessageResponse, ChatSessionResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def generate_streamed_chat_reply(*, system_prompt: str, document_text: str, user_message: str) -> AsyncIterator[str]:
    try:
        from openai import AsyncOpenAI
    except Exception as exc:  # pragma: no cover - fallback for missing dependency
        raise RuntimeError("OpenAI client is not available") from exc

    client = AsyncOpenAI(api_key="")
    # The implementation is intentionally lightweight here; tests monkeypatch this helper.
    prompt = f"{system_prompt}\n\nDocumento:\n{document_text[:12000]}\n\nUsuario: {user_message}"
    response = await client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        stream=True,
    )
    async for event in response:
        if getattr(event, "type", None) == "response.output_text.delta":
            delta = getattr(event, "delta", "")
            if delta:
                yield delta


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(payload: ChatCreateSessionRequest, session: AsyncSession = Depends(get_session)) -> ChatSessionResponse:
    document = await session.get(Document, payload.document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    chat_session = ChatSession(document_id=document.id)
    session.add(chat_session)
    await session.commit()
    await session.refresh(chat_session)
    return ChatSessionResponse(id=chat_session.id, document_id=chat_session.document_id, created_at=chat_session.created_at)


@router.post("/sessions/{session_id}/messages")
async def create_chat_message(session_id: UUID, payload: ChatCreateMessageRequest, request_session: AsyncSession = Depends(get_session)) -> StreamingResponse:
    chat_session = await request_session.get(ChatSession, session_id)
    if chat_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión de chat no encontrada")

    document = await request_session.get(Document, chat_session.document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    user_message = ChatMessage(session_id=chat_session.id, role="user", content=payload.content)
    request_session.add(user_message)
    await request_session.commit()
    await request_session.refresh(user_message)

    system_prompt = (
        "Responde únicamente basándote en el contenido del documento. "
        "Si la respuesta no aparece en el documento, dilo explícitamente y evita inventar información."
    )

    async def event_stream() -> AsyncIterator[str]:
        chunks: list[str] = []
        async for chunk in generate_streamed_chat_reply(
            system_prompt=system_prompt,
            document_text=document.content_text,
            user_message=payload.content,
        ):
            chunks.append(chunk)
            payload_chunk = json.dumps({"delta": chunk})
            yield f"data: {payload_chunk}\n\n"

        yield "event: done\ndata: {}\n\n"
        assistant_message = ChatMessage(session_id=chat_session.id, role="assistant", content="".join(chunks))
        request_session.add(assistant_message)
        await request_session.commit()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_chat_history(session_id: UUID, request_session: AsyncSession = Depends(get_session)) -> list[ChatMessageResponse]:
    chat_session = await request_session.get(ChatSession, session_id)
    if chat_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión de chat no encontrada")

    result = await request_session.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        ChatMessageResponse(id=message.id, session_id=message.session_id, role=message.role, content=message.content, created_at=message.created_at)
        for message in messages
    ]
