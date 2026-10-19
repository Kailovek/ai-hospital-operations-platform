from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ReportRequest(BaseModel):
    report_type: Literal["weekly", "monthly", "custom"]
    period_start: date
    period_end: date
    format: Literal["markdown"] = "markdown"

    @model_validator(mode="after")
    def validate_period(self) -> "ReportRequest":
        if self.period_end < self.period_start:
            raise ValueError("period_end must not be earlier than period_start")
        return self


class ReportTaskSummary(BaseModel):
    task_id: UUID
    kind: Literal["hospital_report"] = "hospital_report"
    status: Literal["queued", "running", "succeeded", "failed", "cancelled"]
    progress: int = Field(ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    reused: bool = False
    error: str | None = None


class ReportStatistics(BaseModel):
    device_total: int
    maintenance_total: int
    devices_by_status: dict[str, int]
    maintenance_by_type: dict[str, int]
    maintenance_by_severity: dict[str, int]


class ReportResult(BaseModel):
    task_id: UUID
    report_type: Literal["weekly", "monthly", "custom"]
    period_start: date
    period_end: date
    format: Literal["markdown"]
    content: str
    statistics: ReportStatistics
    generated_at: datetime
    download_url: str
