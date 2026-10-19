import hashlib
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import KnowledgeChunk, KnowledgeDocument, TaskRecord
from app.modules.knowledge.schemas import SearchHit, TaskSummary
from app.services.document_parser import chunk_document, parse_document
from app.services.retrieval.local_hybrid import search


def ingest_document(
    db: Session, filename: str, content_type: str, content: bytes, title: str | None
) -> TaskSummary:
    checksum = hashlib.sha256(content).hexdigest()
    if db.scalar(select(KnowledgeDocument.id).where(KnowledgeDocument.checksum == checksum)):
        raise AppError(409, "document_duplicate", "This document has already been ingested")
    text = parse_document(filename, content)
    chunks = chunk_document(text)
    if not chunks:
        raise AppError(400, "document_empty", "Document contains no extractable text")
    document = KnowledgeDocument(
        title=(title or Path(filename).stem).strip(),
        filename=Path(filename).name,
        content_type=content_type or "application/octet-stream",
        checksum=checksum,
        chunk_count=len(chunks),
    )
    db.add(document)
    db.flush()
    db.add_all(
        KnowledgeChunk(
            document_id=document.id,
            ordinal=index,
            content=chunk,
            token_count=len(chunk.split()),
        )
        for index, chunk in enumerate(chunks)
    )
    task = TaskRecord(
        kind="knowledge_ingestion",
        status="succeeded",
        progress=100,
        result_json=json.dumps({"document_id": document.id, "chunks": len(chunks)}),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskSummary(
        task_id=task.id,
        status=task.status,
        progress=task.progress,
        created_at=task.created_at,
        updated_at=task.updated_at,
        error=task.error,
    )


def search_knowledge(db: Session, query: str, top_k: int) -> list[SearchHit]:
    return search(db, query, top_k)
