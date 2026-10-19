from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.analysis.schemas import QuestionAnswer, QuestionRequest
from app.modules.knowledge.service import search_knowledge

router = APIRouter(prefix="/analysis", tags=["analysis"])
Database = Annotated[Session, Depends(get_db)]


@router.post("/questions", response_model=QuestionAnswer)
def answer_question(payload: QuestionRequest, db: Database, request: Request) -> QuestionAnswer:
    citations = search_knowledge(db, payload.question, payload.top_k)
    provider = request.app.state.llm_provider
    result = provider.analyze(payload.question, citations)
    return QuestionAnswer(
        answer=str(result["answer"]),
        risk_level=str(result["risk_level"]),
        recommendations=[str(item) for item in result["recommendations"]],
        citations=citations,
        provider=provider.name,
    )
