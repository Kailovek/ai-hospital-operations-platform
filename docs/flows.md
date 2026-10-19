# Data and analysis flows

## Data governance

```mermaid
flowchart LR
    File[CSV / JSON / XLSX] --> Reader[import_reader.py]
    Reader --> Normalize[cleaning.py]
    Normalize --> Dedup[imports/service.py: validate and deduplicate]
    Dedup --> Device[(SQLAlchemy Device table)]
    Device --> Query[devices/service.py: filter and aggregate]
```

## Local hybrid retrieval

```mermaid
flowchart LR
    Upload[PDF / DOCX / TXT / MD] --> Parser[document_parser.py]
    Parser --> Chunk[paragraph-aware chunks]
    Chunk --> Store[(KnowledgeDocument + KnowledgeChunk)]
    Question --> Search[local_hybrid.py]
    Store --> Search
    Search --> Lexical[keyword score]
    Search --> Hash[128-D deterministic feature hash + cosine]
    Lexical --> RRF[Reciprocal Rank Fusion]
    Hash --> RRF
    RRF --> Overlap[term-overlap rerank]
    Overlap --> Citation[ranked chunks and citations]
```

The vector branch is a lightweight deterministic retrieval feature, not neural embeddings. The rerank stage is a transparent heuristic, not a learned model.

## Question answering and reports

```mermaid
flowchart TD
    Q[Question request] --> Search[Knowledge search]
    Search --> Provider[LLM Provider interface]
    Provider --> Mock[Mock Demo response]
    Provider -. Optional configuration .-> HTTP[OpenAI-compatible HTTP]
    Mock --> Answer[Answer + risk + recommendations + citations]
    HTTP --> Answer
    R[Report request] --> Stats[SQL aggregate counts]
    Stats --> Reuse[Look up completed task by request hash]
    Reuse --> Render[Markdown report]
    Render --> Download[Report download]
```
