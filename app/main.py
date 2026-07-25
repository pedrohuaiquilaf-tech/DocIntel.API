from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="DocIntel.API",
        description="API para subir PDFs, extraer texto y conversar con un asistente fundamentado en el documento.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(documents_router)

    from fastapi.exceptions import RequestValidationError
    from fastapi import HTTPException

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.on_event("startup")
    async def on_startup() -> None:
        if settings.database_url:
            await init_db()

    return app


app = create_app()
