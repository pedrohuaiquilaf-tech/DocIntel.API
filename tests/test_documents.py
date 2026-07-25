from pathlib import Path

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_upload_pdf_success(client):
    sample_pdf = Path(__file__).parent / "fixtures" / "sample.pdf"
    with sample_pdf.open("rb") as handle:
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("sample.pdf", handle, "application/pdf")},
        )

    assert response.status_code == status.HTTP_201_CREATED
    payload = response.json()
    assert payload["filename"] == "sample.pdf"
    assert payload["page_count"] == 1
    assert "preview" in payload


@pytest.mark.asyncio
async def test_upload_non_pdf_rejected(client):
    response = await client.post(
        "/api/documents/upload",
        files={"file": ("sample.txt", b"hello", "text/plain")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Solo se aceptan archivos PDF con contenido MIME application/pdf."
