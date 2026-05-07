from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.place import PlaceCreate, PlaceRead, PlaceUpdate
from app.services import place_service

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])


@router.get("", response_model=list[PlaceRead])
async def list_places(
    project_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    is_visited: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await place_service.list_places(db, project_id, skip=skip, limit=limit, is_visited=is_visited)


@router.get("/{place_id}", response_model=PlaceRead)
async def get_place(project_id: int, place_id: int, db: AsyncSession = Depends(get_db)):
    return await place_service.get_place(db, project_id, place_id)


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
async def add_place(
    project_id: int, data: PlaceCreate, db: AsyncSession = Depends(get_db)
):
    return await place_service.add_place(db, project_id, data)


@router.put("/{place_id}", response_model=PlaceRead)
async def update_place(
    project_id: int, place_id: int, data: PlaceUpdate, db: AsyncSession = Depends(get_db)
):
    return await place_service.update_place(db, project_id, place_id, data)
