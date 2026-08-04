from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import CHAR, TypeDecorator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings


class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PGUUID

            return dialect.type_descriptor(PGUUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        if hasattr(value, "hex") and hasattr(value, "version"):
            return uuid.UUID(str(value))
        if isinstance(value, str):
            return uuid.UUID(value)
        return uuid.UUID(str(value))


engine: Any = None
AsyncSessionLocal: Any = None
Base = declarative_base()


def get_engine() -> Any:
    global engine, AsyncSessionLocal
    if engine is None:
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL must be configured before initializing the database engine.")
        engine = create_async_engine(settings.database_url, future=True, echo=False)
        AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    return engine


async def get_session() -> AsyncSession:
    if AsyncSessionLocal is None:
        get_engine()
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
