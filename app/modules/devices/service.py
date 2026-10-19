from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import Device
from app.modules.devices.schemas import (
    DeviceCreate,
    DevicePage,
    DeviceRead,
    DeviceStatistics,
    DeviceUpdate,
)


def create_device(db: Session, payload: DeviceCreate) -> Device:
    device = Device(**payload.model_dump())
    db.add(device)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppError(
            409,
            "device_asset_code_conflict",
            "A device with this asset code already exists",
        ) from exc
    db.refresh(device)
    return device


def list_devices(
    db: Session,
    page: int,
    page_size: int,
    status: str | None,
    keyword: str | None,
) -> DevicePage:
    filters = []
    if status:
        filters.append(Device.status == status)
    if keyword:
        pattern = f"%{keyword.strip()}%"
        filters.append(or_(Device.asset_code.ilike(pattern), Device.name.ilike(pattern)))
    total = db.scalar(select(func.count(Device.id)).where(*filters)) or 0
    rows = db.scalars(
        select(Device)
        .where(*filters)
        .order_by(Device.created_at.desc(), Device.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DevicePage(
        page=page,
        page_size=page_size,
        total=total,
        items=[DeviceRead.model_validate(row) for row in rows],
    )


def get_device(db: Session, device_id: str) -> Device:
    device = db.get(Device, device_id)
    if device is None:
        raise AppError(404, "device_not_found", "Device was not found")
    return device


def update_device(db: Session, device_id: str, payload: DeviceUpdate) -> Device:
    device = get_device(db, device_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def device_statistics(db: Session) -> DeviceStatistics:
    by_status = dict(db.execute(select(Device.status, func.count()).group_by(Device.status)).all())
    by_category = dict(
        db.execute(select(Device.category, func.count()).group_by(Device.category)).all()
    )
    return DeviceStatistics(
        total=sum(by_status.values()), by_status=by_status, by_category=by_category
    )
