from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.models import Document
from app.schemas import DocumentPreview
from app.utils.pdf import DocumentExtractionError, extract_text_from_pdf

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentPreview, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> DocumentPreview:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos PDF con contenido MIME application/pdf.",
        )

    payload = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(payload) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {settings.max_upload_size_mb} MB.",
        )

    try:
        content_text, page_count = extract_text_from_pdf(payload)
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    document = Document(filename=file.filename, content_text=content_text, page_count=page_count)
    session.add(document)
    await session.commit()
    await session.refresh(document)

    preview = content_text[:1024]
    return DocumentPreview(
        id=document.id,
        filename=document.filename,
        page_count=document.page_count,
        preview=preview,
        uploaded_at=document.uploaded_at,
    )
