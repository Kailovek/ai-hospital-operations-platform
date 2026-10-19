from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.reports.schemas import ReportRequest, ReportResult, ReportTaskSummary
from app.modules.reports.service import create_report, get_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportTaskSummary, status_code=status.HTTP_202_ACCEPTED)
def submit_report(
    payload: ReportRequest, db: Annotated[Session, Depends(get_db)]
) -> ReportTaskSummary:
    return create_report(db, payload)


@router.get("/{task_id}", response_model=ReportResult)
def read_report(task_id: UUID, db: Annotated[Session, Depends(get_db)]) -> ReportResult:
    return get_report(db, str(task_id))


@router.get("/{task_id}/download")
def download_report(task_id: UUID, db: Annotated[Session, Depends(get_db)]) -> Response:
    report = get_report(db, str(task_id))
    return Response(
        content=report.content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="report-{task_id}.md"'},
    )
