from __future__ import annotations

import fitz


class DocumentExtractionError(ValueError):
    pass


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise DocumentExtractionError("El archivo no es un PDF válido") from exc

    page_count = doc.page_count
    if page_count == 0:
        raise DocumentExtractionError("El PDF no contiene páginas válidas")

    text_chunks: list[str] = []
    for page in doc:
        text_chunks.append(page.get_text())

    full_text = "\n".join(text_chunks).strip()
    if not full_text:
        raise DocumentExtractionError(
            "No se encontró texto extraíble en el PDF. Los documentos escaneados sin OCR no son compatibles en esta versión."
        )

    return full_text, page_count
