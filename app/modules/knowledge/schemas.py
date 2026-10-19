from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class TaskSummary(BaseModel):
    task_id: UUID
    status: Literal["queued", "running", "succeeded", "failed", "cancelled"]
    progress: int = Field(ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    error: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchHit(BaseModel):
    chunk_id: UUID
    document_id: UUID
    title: str
    content: str
    score: float
    citation: str
    scores: dict[str, float]
