from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db import Base, get_session
from app.main import create_app


@pytest.fixture(scope="session")
def async_engine() -> object:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True, echo=False)

    async def init_models() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture(scope="function")
def async_session(async_engine) -> AsyncSession:
    TestSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)
    session = TestSessionLocal()
    yield session
    asyncio.run(session.close())


@pytest.fixture(scope="function")
def app(async_session: AsyncSession) -> FastAPI:
    application = create_app()

    async def get_test_session() -> AsyncSession:
        yield async_session

    application.dependency_overrides[get_session] = get_test_session
    return application


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
