# Modules and boundaries

| Path | Responsibility | Depends on |
| --- | --- | --- |
| `app/main.py` | FastAPI application factory, startup, routers, health | Settings, SQLAlchemy, LLM Provider |
| `app/core/config.py` | Environment settings and runtime validation | Pydantic settings |
| `app/core/errors.py` | Request IDs and normalized error responses | FastAPI |
| `app/db/models.py` | Device, maintenance, document, chunk and task tables | SQLAlchemy |
| `app/modules/devices/` | Device creation, lookup, update, filtering and statistics | Database session |
| `app/modules/maintenance/` | Operations records and summaries | Device and maintenance tables |
| `app/modules/imports/` | CSV/JSON/XLSX import | Reader, normalization, devices table |
| `app/modules/knowledge/` | Document ingestion and knowledge search | Parser, local hybrid retrieval, document tables |
| `app/modules/analysis/` | Grounded question API | Knowledge search, LLM Provider |
| `app/modules/reports/` | Aggregate reports and Markdown export | Device, maintenance and task tables |
| `app/services/retrieval/local_hybrid.py` | Hashed features, keyword scoring, RRF, overlap rerank | Stored knowledge chunks |
| `app/services/llm/providers.py` | Reference-response and OpenAI-compatible provider implementations | HTTPX, settings |

Persistence uses SQLAlchemy with SQLite. Retrieval combines deterministic 128-dimensional feature-hash vectors, lexical scores, RRF ranking fusion, and query-term coverage reranking. Results include source citations and scores for every stage.

Knowledge ingestion and report submission complete synchronously and return `202` with task metadata. Report reuse looks up a completed SQL task by the request digest, connecting result storage, query, and export through a common task ID.
