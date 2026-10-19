from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DeviceStatus = Literal["active", "maintenance", "retired"]


class DeviceCreate(BaseModel):
    asset_code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    category: str = Field(min_length=1, max_length=64)
    department: str = Field(min_length=1, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=128)
    model: str | None = Field(default=None, max_length=128)
    status: DeviceStatus = "active"


class DeviceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    department: str | None = Field(default=None, min_length=1, max_length=64)
    manufacturer: str | None = Field(default=None, max_length=128)
    model: str | None = Field(default=None, max_length=128)
    status: DeviceStatus | None = None


class DeviceRead(DeviceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class DevicePage(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[DeviceRead]


class DeviceStatistics(BaseModel):
    total: int
    by_status: dict[str, int]
    by_category: dict[str, int]
