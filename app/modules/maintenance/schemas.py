from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

RecordType = Literal["inspection", "maintenance", "fault", "repair"]
Severity = Literal["low", "medium", "high", "critical"]


class MaintenanceCreate(BaseModel):
    device_id: UUID
    record_type: RecordType
    severity: Severity
    description: str = Field(min_length=1, max_length=4000)
    action_taken: str | None = Field(default=None, max_length=4000)
    occurred_at: datetime


class MaintenanceRead(MaintenanceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime


class MaintenancePage(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[MaintenanceRead]


class MaintenanceStatistics(BaseModel):
    total: int
    by_type: dict[str, int]
    by_severity: dict[str, int]
