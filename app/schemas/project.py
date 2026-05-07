from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from app.schemas.place import PlaceCreate, PlaceRead


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    places: Optional[List[PlaceCreate]] = None


class ProjectRead(ProjectBase):
    id: int
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime
    places: List[PlaceRead] = []

    model_config = {"from_attributes": True}


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
