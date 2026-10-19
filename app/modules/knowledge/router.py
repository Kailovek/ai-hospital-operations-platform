from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.knowledge import service
from app.modules.knowledge.schemas import SearchHit, SearchRequest, TaskSummary

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
Database = Annotated[Session, Depends(get_db)]
DocumentFile = Annotated[UploadFile, File()]
DocumentTitle = Annotated[str | None, Form()]


@router.post("/documents", response_model=TaskSummary, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    db: Database, file: DocumentFile, title: DocumentTitle = None
) -> TaskSummary:
    content = await file.read()
    return service.ingest_document(
        db, file.filename or "document", file.content_type or "", content, title
    )


@router.post("/search", response_model=list[SearchHit])
def search_knowledge(payload: SearchRequest, db: Database) -> list[SearchHit]:
    return service.search_knowledge(db, payload.query, payload.top_k)
