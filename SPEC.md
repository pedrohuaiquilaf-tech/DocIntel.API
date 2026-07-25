# DocIntel.API — Especificación Técnica

## Resumen
API de "Document Intelligence": permite subir un PDF, extraer su contenido, y conversar con un asistente de IA cuyas respuestas están fundamentadas (grounded) en ese documento, con streaming de respuestas y persistencia del historial de chat.

**Propósito:** Proyecto de portfolio freelance. Debe verse profesional, production-ready, y demostrar patrones reales de arquitectura de IA aplicada (no un wrapper trivial de OpenAI).

---

## Stack Técnico

| Categoría | Tecnología |
|---|---|
| Framework | FastAPI |
| Lenguaje | Python 3.12 |
| ORM | SQLAlchemy 2.0 (async) |
| Base de datos | PostgreSQL 16 |
| Migraciones | Alembic |
| Extracción PDF | PyMuPDF (fitz) |
| IA / LLM | OpenAI API (cliente async, streaming), configurable vía env var |
| Validación | Pydantic v2 |
| Testing | pytest + pytest-asyncio + httpx (AsyncClient) |
| Frontend | Vue 3 + Vite + Pinia |
| Contenedores | Docker + Docker Compose |

---

## Modelo de Datos

### `Document`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| filename | string | |
| content_text | text | Texto extraído del PDF |
| page_count | int | |
| uploaded_at | datetime | |

### `ChatSession`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| document_id | UUID | FK → Document, ON DELETE CASCADE |
| created_at | datetime | |

### `ChatMessage`
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID | PK |
| session_id | UUID | FK → ChatSession, ON DELETE CASCADE |
| role | string | `"user"` \| `"assistant"` |
| content | text | |
| created_at | datetime | |

---

## Endpoints

### Documentos
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/documents/upload` | Sube un PDF, valida tipo/tamaño, extrae texto, retorna preview |
| GET | `/api/documents/{id}` | Detalle de un documento |
| GET | `/api/documents` | Lista paginada (`page`, `page_size`) |

### Chat
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/chat/sessions` | Crea sesión de chat ligada a un `document_id` |
| POST | `/api/chat/sessions/{id}/messages` | Envía mensaje, respuesta **en streaming (SSE)**, persiste historial al completar |
| GET | `/api/chat/sessions/{id}/messages` | Historial completo de la sesión |

### Salud
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Health check simple |

---

## Reglas de Negocio / Detalles de Implementación

1. **Validación de upload:** solo `application/pdf`; rechazar con 400 si no. Límite de tamaño configurable vía env var (`MAX_UPLOAD_SIZE_MB`), rechazar con 413 si excede.
2. **Extracción de texto:** si el PDF no tiene texto extraíble (ej. escaneado sin OCR), retornar 422 con mensaje claro — no fallar silenciosamente.
3. **Streaming de chat:** usar Server-Sent Events (`text/event-stream`). Cada chunk del modelo se envía como `data: {"delta": "..."}\n\n`. Al finalizar, enviar `event: done\ndata: {}\n\n` y persistir el mensaje del usuario + la respuesta completa ensamblada del asistente.
4. **Contexto del LLM:** el prompt de sistema debe instruir al modelo a responder solo en base al contenido del documento, y declarar explícitamente cuando la respuesta no está en el documento (evitar alucinaciones). Truncar el texto del documento a un límite seguro de caracteres/tokens antes de enviarlo al modelo.
5. **Manejo de errores global:** middleware de excepciones que devuelva errores estructurados (tipo RFC 7807), igual que en CRM.API.
6. **Sin credenciales hardcodeadas:** todo secreto (API key de OpenAI, connection string) vía variables de entorno. Incluir `.env.example` sin valores reales.
7. **CORS:** habilitado para desarrollo (frontend en puerto distinto al backend).

---

## Testing Requerido

- Extracción de PDF: caso exitoso, PDF inválido, PDF sin texto extraíble.
- Documentos: upload exitoso, rechazo de tipo no-PDF, get por ID (existente/no existente), listado paginado.
- Chat: creación de sesión (documento existente/no existente), historial vacío en sesión nueva, envío de mensaje con streaming mockeado (no llamar a la API real de OpenAI en tests) y verificación de persistencia correcta del historial.
- Usar SQLite in-memory para tests (no requiere Postgres corriendo).

---

## Docker

- `docker-compose.yml` con dos servicios: `postgres` (con healthcheck) y `api` (espera a que Postgres esté healthy, corre migraciones de Alembic automáticamente al iniciar, luego levanta uvicorn).
- Dockerfile con multi-stage no es necesario; imagen `python:3.12-slim` es suficiente.

---

## Frontend (Vue 3)

Interfaz mínima de dos pantallas:
1. **Upload:** drag-and-drop o selector de archivo PDF.
2. **Chat:** una vez subido el documento, panel de chat con historial visible y streaming de la respuesta en tiempo real (consumir el SSE del backend con `fetch` + `ReadableStream`, no `EventSource` nativo porque este último no soporta POST con body).

No requiere routing (Vue Router) — es una experiencia de una sola pantalla que cambia de estado (upload → chat).

---

## README esperado (nivel de referencia: CRM.API)

Debe incluir: Tech Stack, Architecture (diagrama simple), Domain Model, API Endpoints (tablas), Key Implementation Details, Getting Started (Docker Compose + desarrollo local), Running Tests, Future Improvements, About, License.

**Nota de discreción:** no mencionar OSG, Bedrock, Claude Sonnet, ni ningún nombre de proyecto interno. El dominio de los documentos debe ser genérico (cualquier PDF: contratos, reportes, papers) — no insurance/insurtech.

---

## Fuera de Alcance (v1)

- Autenticación/autorización (queda para una v2 si se decide)
- Multi-tenancy
- Soporte para OCR de PDFs escaneados
- Rate limiting
- Despliegue a un proveedor cloud específico
