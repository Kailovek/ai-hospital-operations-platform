from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.maintenance import service
from app.modules.maintenance.schemas import (
    MaintenanceCreate,
    MaintenancePage,
    MaintenanceRead,
    MaintenanceStatistics,
)

router = APIRouter(prefix="/maintenance-records", tags=["maintenance"])
Database = Annotated[Session, Depends(get_db)]


@router.get("", response_model=MaintenancePage)
def list_records(
    db: Database,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    record_type: str | None = None,
) -> MaintenancePage:
    return service.list_records(
        db, page, page_size, str(device_id) if device_id else None, record_type
    )


@router.post("", response_model=MaintenanceRead, status_code=status.HTTP_201_CREATED)
def create_record(payload: MaintenanceCreate, db: Database):
    return service.create_record(db, payload)


@router.get("/statistics", response_model=MaintenanceStatistics)
def get_maintenance_statistics(db: Database) -> MaintenanceStatistics:
    return service.maintenance_statistics(db)
