from typing import Any

DEVICE_FIELD_ALIASES = {
    "asset_code": "asset_code",
    "assetcode": "asset_code",
    "device_code": "asset_code",
    "name": "name",
    "devicename": "name",
    "device_name": "name",
    "category": "category",
    "device_type": "category",
    "department": "department",
    "manufacturer": "manufacturer",
    "vendor": "manufacturer",
    "model": "model",
    "status": "status",
}


def normalize_device_row(row: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    normalized: dict[str, Any] = {}
    for source_key, value in row.items():
        compact_key = str(source_key).strip().replace("-", "_").replace(" ", "").lower()
        target_key = DEVICE_FIELD_ALIASES.get(compact_key)
        if target_key is None:
            continue
        if isinstance(value, str):
            value = value.strip()
        normalized[target_key] = value if value != "" else None

    for required in ("asset_code", "name", "category", "department"):
        if not normalized.get(required):
            return None, f"{required} is required"
    normalized["asset_code"] = str(normalized["asset_code"]).upper()
    normalized["status"] = str(normalized.get("status") or "active").lower()
    if normalized["status"] not in {"active", "maintenance", "retired"}:
        return None, "status must be active, maintenance, or retired"
    return normalized, None
