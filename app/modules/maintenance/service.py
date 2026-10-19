from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import Device, MaintenanceRecord
from app.modules.maintenance.schemas import (
    MaintenanceCreate,
    MaintenancePage,
    MaintenanceRead,
    MaintenanceStatistics,
)


def create_record(db: Session, payload: MaintenanceCreate) -> MaintenanceRecord:
    if db.get(Device, str(payload.device_id)) is None:
        raise AppError(404, "device_not_found", "Device was not found")
    record = MaintenanceRecord(
        **payload.model_dump(exclude={"device_id"}), device_id=str(payload.device_id)
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_records(
    db: Session, page: int, page_size: int, device_id: str | None, record_type: str | None
) -> MaintenancePage:
    filters = []
    if device_id:
        filters.append(MaintenanceRecord.device_id == device_id)
    if record_type:
        filters.append(MaintenanceRecord.record_type == record_type)
    total = db.scalar(select(func.count(MaintenanceRecord.id)).where(*filters)) or 0
    rows = db.scalars(
        select(MaintenanceRecord)
        .where(*filters)
        .order_by(MaintenanceRecord.occurred_at.desc(), MaintenanceRecord.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return MaintenancePage(
        page=page,
        page_size=page_size,
        total=total,
        items=[MaintenanceRead.model_validate(row) for row in rows],
    )


def maintenance_statistics(db: Session) -> MaintenanceStatistics:
    by_type = dict(
        db.execute(
            select(MaintenanceRecord.record_type, func.count()).group_by(
                MaintenanceRecord.record_type
            )
        ).all()
    )
    by_severity = dict(
        db.execute(
            select(MaintenanceRecord.severity, func.count()).group_by(MaintenanceRecord.severity)
        ).all()
    )
    return MaintenanceStatistics(
        total=sum(by_type.values()), by_type=by_type, by_severity=by_severity
    )
