from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Device
from app.modules.imports.schemas import ImportResult
from app.services.cleaning import normalize_device_row


def import_devices(db: Session, rows: list[tuple[int, dict[str, Any]]]) -> ImportResult:
    result = ImportResult(
        received=len(rows), inserted=0, updated=0, rejected=0, duplicates=0, errors=[]
    )
    seen: set[str] = set()
    for row_number, raw in rows:
        cleaned, error = normalize_device_row(raw)
        if error:
            result.rejected += 1
            if len(result.errors) < 50:
                result.errors.append(f"row {row_number}: {error}")
            continue
        assert cleaned is not None
        asset_code = cleaned["asset_code"]
        if asset_code in seen:
            result.duplicates += 1
            continue
        seen.add(asset_code)
        existing = db.scalar(select(Device).where(Device.asset_code == asset_code))
        if existing is None:
            db.add(Device(**cleaned))
            result.inserted += 1
        else:
            for key, value in cleaned.items():
                if key != "asset_code" and value is not None:
                    setattr(existing, key, value)
            result.updated += 1
    db.commit()
    return result
