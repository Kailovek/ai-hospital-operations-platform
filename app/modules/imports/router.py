from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.imports.schemas import ImportResult
from app.modules.imports.service import import_devices
from app.services.import_reader import read_import_rows

router = APIRouter(prefix="/imports", tags=["imports"])
Database = Annotated[Session, Depends(get_db)]
ImportFile = Annotated[UploadFile, File()]


@router.post("/devices", response_model=ImportResult)
async def upload_devices(db: Database, file: ImportFile) -> ImportResult:
    content = await file.read()
    rows = read_import_rows(file.filename or "", content)
    return import_devices(db, rows)
