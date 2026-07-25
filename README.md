# DocIntel.API

Document Intelligence API — FastAPI + PostgreSQL + OpenAI.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL 16
- PyMuPDF para extracción de texto de PDFs
- OpenAI API para chat fundamentado
- Docker + Docker Compose

## Arquitectura

- `app/main.py`: aplicación FastAPI y configuración de enrutadores
- `app/config.py`: settings y variables de entorno
- `app/db.py`: motor async y sesión SQLAlchemy
- `app/models.py`: entidades `Document`, `ChatSession`, `ChatMessage`
- `app/routes/`: endpoints REST
- `app/utils/pdf.py`: lógica de extracción de texto de PDF

## Endpoints implementados

- `GET /health`
- `POST /api/documents/upload`

## Getting started

1. Copia `.env.example` a `.env` y ajusta los valores.
2. Levanta los servicios con Docker Compose:

```bash
docker compose up --build
```

3. La API estará disponible en `http://localhost:8000`.

## Desarrollo local

```bash
python -m pip install -e .
uvicorn app.main:app --reload
```

## Tests

```bash
python -m pytest
```

## Future improvements

- Implementar SSE para chat streaming
- Agregar rutas de chat y persistencia de mensajes
- Configurar migraciones Alembic reales
- Crear frontend Vue 3

## License

MIT
