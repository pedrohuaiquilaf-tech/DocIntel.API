from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import status
from sqlalchemy import select

from app.models import ChatMessage, ChatSession, Document


@pytest.mark.anyio
async def test_create_chat_session_for_existing_document(client, async_session):
    document = Document(filename="sample.pdf", content_text="Contenido de prueba del documento", page_count=1)
    async_session.add(document)
    await async_session.commit()
    await async_session.refresh(document)

    response = await client.post("/api/chat/sessions", json={"document_id": str(document.id)})

    assert response.status_code == status.HTTP_201_CREATED
    payload = response.json()
    assert payload["document_id"] == str(document.id)
    assert payload["id"]


@pytest.mark.anyio
async def test_get_chat_history_returns_empty_for_new_session(client, async_session):
    document = Document(filename="sample.pdf", content_text="Contenido de prueba del documento", page_count=1)
    async_session.add(document)
    await async_session.commit()
    await async_session.refresh(document)

    session = ChatSession(document_id=document.id)
    async_session.add(session)
    await async_session.commit()
    await async_session.refresh(session)

    response = await client.get(f"/api/chat/sessions/{session.id}/messages")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.anyio
async def test_stream_chat_message_persists_history(client, async_session, monkeypatch):
    document = Document(filename="sample.pdf", content_text="Contenido de prueba del documento", page_count=1)
    async_session.add(document)
    await async_session.commit()
    await async_session.refresh(document)

    session = ChatSession(document_id=document.id)
    async_session.add(session)
    await async_session.commit()
    await async_session.refresh(session)

    async def fake_streaming_reply(*, system_prompt: str, document_text: str, user_message: str, api_key: str):
        assert api_key == "fake-key"
        yield "Hola"
        yield " desde el mock"

    import app.routes.chat as chat_routes

    monkeypatch.setattr(chat_routes, "generate_streamed_chat_reply", fake_streaming_reply)
    monkeypatch.setattr(chat_routes.settings, "openai_api_key", "fake-key")

    response = await client.post(
        f"/api/chat/sessions/{session.id}/messages",
        json={"content": "¿Qué dice el documento?"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.text
    assert 'data: {"delta": "Hola"}' in body
    assert 'data: {"delta": " desde el mock"}' in body
    assert "event: done" in body

    result = await async_session.execute(select(ChatMessage).where(ChatMessage.session_id == session.id))
    persisted_messages = result.scalars().all()
    assert len(persisted_messages) == 2
    assert persisted_messages[0].role == "user"
    assert persisted_messages[1].role == "assistant"
    assert persisted_messages[1].content == "Hola desde el mock"


@pytest.mark.anyio
async def test_chat_message_returns_clear_error_without_openai_key(client, async_session, monkeypatch):
    document = Document(filename="sample.pdf", content_text="Contenido de prueba del documento", page_count=1)
    async_session.add(document)
    await async_session.commit()
    await async_session.refresh(document)

    session = ChatSession(document_id=document.id)
    async_session.add(session)
    await async_session.commit()
    await async_session.refresh(session)

    import app.routes.chat as chat_routes

    monkeypatch.setattr(chat_routes.settings, "openai_api_key", None)

    response = await client.post(
        f"/api/chat/sessions/{session.id}/messages",
        json={"content": "¿Qué dice el documento?"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    payload = response.json()
    assert payload["detail"] == "OpenAI API key is required to generate chat responses."
