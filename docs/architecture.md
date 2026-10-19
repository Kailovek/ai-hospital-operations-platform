# Architecture

## Runtime architecture

```mermaid
flowchart LR
    Client[Swagger / REST client] --> API[FastAPI API layer]
    API --> Domain[Device, maintenance, import, report services]
    API --> RAG[Document ingestion and hybrid retrieval]
    API --> LLM[LLM provider interface]
    Domain --> SQL[(SQLite via SQLAlchemy)]
    RAG --> SQL
    LLM --> Provider[Provider implementations]
    Domain --> Export[Markdown report]
```

The application separates HTTP routing, domain services, persistence, retrieval, and model-provider protocols. SQLAlchemy stores equipment, maintenance, document, and task records. Retrieval combines feature-hash vectors, keyword scoring, RRF, and term-overlap reranking; analysis assembles the resulting context and citations into a structured response.

## Model provider boundary

```mermaid
flowchart TB
    API[Analysis router] --> Search[Local knowledge search]
    Search --> SQL[(SQLite knowledge chunks)]
    API --> Provider{LLM Provider interface}
    Provider --> Reference[Reference-response implementation]
    Provider --> HTTP[OpenAI-compatible HTTP adapter]
    HTTP --> DeepSeek[DeepSeek-compatible API]
    HTTP --> Ollama[Ollama-compatible API]
    HTTP --> vLLM[vLLM-compatible API]
```

`build_provider()` centralizes provider selection. The analysis service calls the same `analyze(question, contexts)` interface, while the HTTP adapter encapsulates endpoint formats, request timeouts, JSON parsing, and required-field checks.

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
- Provider isolation: model protocols and credentials belong to the provider layer; business code calls a common interface.
- Health reporting: the endpoint exposes database readiness, runtime mode, retrieval mode, and dependency status.
- Input bounds: document/import content is checked against 15/10 MB limits after reading; page size and import error details are bounded. Chunking follows paragraph boundaries, so a very long paragraph can exceed the target chunk size.
- Privacy by construction: generated reports aggregate records and do not enumerate device identifiers.
