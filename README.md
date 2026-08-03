# DocIntel.API

Document Intelligence API — FastAPI + PostgreSQL + OpenAI.

A production-style portfolio project for processing PDF documents, extracting their content, and enabling grounded chat over the document with streaming responses.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL 16
- Alembic for migrations
- PyMuPDF for PDF text extraction
- OpenAI API for grounded chat responses
- Docker + Docker Compose
- Pytest + httpx + pytest-asyncio for testing

## Architecture

A simple layered architecture keeps the API, domain models, persistence, and document/LLM integration separated:

- `app/main.py`: FastAPI application and lifespan lifecycle
- `app/config.py`: environment-based configuration
- `app/db.py`: async SQLAlchemy engine and session factory
- `app/models.py`: domain entities for documents and chat
- `app/routes/`: REST and streaming endpoints
- `app/utils/pdf.py`: PDF extraction logic
- `alembic/`: real database migration setup

## Domain Model

### Document
- `id`: UUID primary key
- `filename`: original PDF name
- `content_text`: extracted text from the PDF
- `page_count`: number of pages
- `uploaded_at`: upload timestamp

### ChatSession
- `id`: UUID primary key
- `document_id`: foreign key to `Document`
- `created_at`: session creation timestamp
- One document can have many chat sessions

### ChatMessage
- `id`: UUID primary key
- `session_id`: foreign key to `ChatSession`
- `role`: `user` or `assistant`
- `content`: message text
- `created_at`: timestamp

## API Endpoints

### Documents
- `GET /health`
- `POST /api/documents/upload`
- `GET /api/documents/{id}`
- `GET /api/documents`

### Chat
- `POST /api/chat/sessions`
- `POST /api/chat/sessions/{id}/messages` (streaming SSE)
- `GET /api/chat/sessions/{id}/messages`

## Key Implementation Details

### Streaming SSE
The chat endpoint uses Server-Sent Events with the format:

```text
data: {"delta": "..."}

```

Each chunk of the assistant response is emitted as a SSE event. The stream ends with:

```text
event: done
data: {}

```

### Why lifespan instead of `on_event`
The application uses FastAPI lifespan to manage startup and shutdown hooks in a modern, explicit way. This avoids deprecated startup/shutdown event handling and keeps initialization logic easier to reason about.

### Grounded prompt behavior
The system prompt instructs the LLM to answer only from the document contents and to explicitly say when the answer is not present in the source text. This helps prevent hallucinations and keeps the assistant grounded in the uploaded document.

### Document truncation before LLM calls
Before sending the document content to the model, the text is truncated to a safe size to avoid oversized prompts and keep requests reliable and efficient.

## Getting Started

### Docker Compose
Run the full stack with PostgreSQL and the API:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Local development

```bash
python -m pip install -e .
uvicorn app.main:app --reload
```

If you want to work with the database locally, make sure your `.env` file contains the expected values from `.env.example`.

### Running tests

```bash
python -m pytest
```

## Future Improvements

- Build the Vue 3 frontend experience for upload and chat

## About

This project is a generic document intelligence portfolio piece. It demonstrates applied AI patterns such as PDF ingestion, text extraction, grounded chat over a document, and real-time streaming responses using FastAPI, PostgreSQL, and OpenAI.

## License

MIT
