from pydantic import BaseModel, Field

from app.modules.knowledge.schemas import SearchHit


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    device_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class QuestionAnswer(BaseModel):
    answer: str
    risk_level: str
    recommendations: list[str]
    citations: list[SearchHit]
    provider: str
