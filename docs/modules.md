# Modules and boundaries

| Path | Responsibility | Depends on |
| --- | --- | --- |
| `app/main.py` | FastAPI application factory, startup, routers, health | Settings, SQLAlchemy, LLM Provider |
| `app/core/config.py` | Environment settings and Demo validation | Pydantic settings |
| `app/core/errors.py` | Request IDs and normalized error responses | FastAPI |
| `app/db/models.py` | Device, maintenance, document, chunk and task tables | SQLAlchemy |
| `app/modules/devices/` | Device CRUD, filtering and statistics | Database session |
| `app/modules/maintenance/` | Operations records and summaries | Device and maintenance tables |
| `app/modules/imports/` | CSV/JSON/XLSX import | Reader, normalization, devices table |
| `app/modules/knowledge/` | Document ingestion and knowledge search | Parser, local hybrid retrieval, document tables |
| `app/modules/analysis/` | Grounded question API | Knowledge search, LLM Provider |
| `app/modules/reports/` | Aggregate reports and Markdown export | Device, maintenance and task tables |
| `app/services/retrieval/local_hybrid.py` | Hashed features, keyword scoring, RRF, overlap rerank | Stored knowledge chunks |
| `app/services/llm/providers.py` | Mock and OpenAI-compatible provider implementations | HTTPX, settings |

The Demo path uses SQLite and a deterministic 128-dimensional feature-hash vector. It does not compute model embeddings or write vectors to Milvus. The rerank stage scores query-term overlap; it is not a learned reranker.

Knowledge ingestion and report submission return `202` with a task record, but both execute synchronously in the current implementation. Report reuse searches previously completed task records in SQL; Redis is not used.
