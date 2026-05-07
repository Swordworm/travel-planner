from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlaceCreate(BaseModel):
    external_id: str


class PlaceRead(BaseModel):
    id: int
    project_id: int
    external_id: str
    notes: Optional[str] = None
    is_visited: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None
