# Architecture

## Demo runtime

```mermaid
flowchart LR
    Client[Swagger / REST client] --> API[FastAPI API layer]
    API --> Domain[Device, maintenance, import, report services]
    API --> RAG[Document ingestion and hybrid retrieval]
    API --> LLM[LLM provider interface]
    Domain --> SQL[(SQLite via SQLAlchemy)]
    RAG --> SQL
    LLM --> Mock[Deterministic Mock provider]
    Domain --> Export[Markdown report]
```

Demo mode keeps the complete application workflow local: SQLite provides persistence, a deterministic hashed vector plus keyword score implements hybrid retrieval, reciprocal-rank fusion combines candidates, token overlap reranks results, and the Mock provider returns structured grounded answers. It needs no model weights, GPU, API key, Redis, or Milvus.

## Model provider boundary

```mermaid
flowchart TB
    API[Analysis router] --> Search[Local knowledge search]
    Search --> SQL[(SQLite knowledge chunks)]
    API --> Provider{LLM Provider interface}
    Provider --> Mock[Mock / verified Demo]
    Provider -. HTTP adapter, unverified .-> DeepSeek[DeepSeek-compatible API]
    Provider -. HTTP adapter, unverified .-> Ollama[Ollama-compatible API]
    Provider -. HTTP adapter, unverified .-> vLLM[vLLM-compatible API]
```

There are no Redis or Milvus runtime adapters. MySQL is a SQLAlchemy configuration possibility with an optional driver, not a verified deployment path. The fine-tuning service is an independent portfolio repository; this application does not call it.

## Knowledge workflow

```mermaid
sequenceDiagram
    participant U as Client
    participant A as FastAPI
    participant P as Parser
    participant D as SQL store
    participant R as Hybrid retriever
    participant L as LLM provider
    U->>A: Upload PDF/DOCX/TXT/Markdown
    A->>P: Parse and chunk
    P->>D: Save document metadata and chunks
    U->>A: Ask operations question
    A->>R: Keyword + hashed-vector retrieval
    R->>R: RRF fusion + term-overlap rerank
    R-->>A: Ranked chunks and citations
    A->>L: Structured grounded prompt
    L-->>A: JSON answer
    A-->>U: Answer + risk + recommendations + citations
```

## Design decisions

- API-first: stable `/api/v1` resources and generated Swagger documentation.
- Provider isolation: business code does not read API keys or call a vendor SDK directly.
- Health reports SQLite readiness, `cache: disabled`, and `vector_store: local` in Demo. These values do not imply Redis or Milvus availability.
- Input bounds: document/import content is checked against 15/10 MB limits after reading; page size and import error details are bounded. Chunking follows paragraph boundaries, so a very long paragraph can exceed the target chunk size.
- Privacy by construction: generated reports aggregate records and do not enumerate device identifiers.
