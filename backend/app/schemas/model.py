import datetime as dt

from pydantic import BaseModel


class ModelOut(BaseModel):
    id: int
    name: str
    algorithm: str
    version: str
    is_active: bool
    trained_at: dt.datetime | None = None
    metrics: dict | None = None
