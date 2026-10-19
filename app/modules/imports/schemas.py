from pydantic import BaseModel


class ImportResult(BaseModel):
    received: int
    inserted: int
    updated: int
    rejected: int
    duplicates: int
    errors: list[str]
