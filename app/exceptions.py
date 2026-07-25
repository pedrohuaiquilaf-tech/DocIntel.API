from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status


def problem_detail(status_code: int, title: str, detail: str, instance: str | None = None) -> dict[str, object]:
    problem = {
        "type": "about:blank",
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    if instance:
        problem["instance"] = instance
    return problem


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    payload = problem_detail(
        status_code=exc.status_code,
        title=exc.detail if isinstance(exc.detail, str) else exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url),
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    message = "; ".join(error.get("msg", "invalid") for error in errors)
    payload = problem_detail(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        title="Request validation failed",
        detail=message,
        instance=str(request.url),
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    payload = problem_detail(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title="Internal server error",
        detail="Ocurrió un error inesperado. Por favor intente nuevamente.",
        instance=str(request.url),
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)
