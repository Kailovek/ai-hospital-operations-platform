from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.devices import service
from app.modules.devices.schemas import (
    DeviceCreate,
    DevicePage,
    DeviceRead,
    DeviceStatistics,
    DeviceUpdate,
)

router = APIRouter(prefix="/devices", tags=["devices"])
Database = Annotated[Session, Depends(get_db)]


@router.get("", response_model=DevicePage)
def list_devices(
    db: Database,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None, min_length=1, max_length=128),
) -> DevicePage:
    return service.list_devices(db, page, page_size, status_filter, keyword)


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(payload: DeviceCreate, db: Database):
    return service.create_device(db, payload)


@router.get("/statistics", response_model=DeviceStatistics)
def get_device_statistics(db: Database) -> DeviceStatistics:
    return service.device_statistics(db)


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: UUID, db: Database):
    return service.get_device(db, str(device_id))


@router.patch("/{device_id}", response_model=DeviceRead)
def update_device(device_id: UUID, payload: DeviceUpdate, db: Database):
    return service.update_device(db, str(device_id), payload)
