from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.place import Place
from app.models.project import Project
from app.schemas.place import PlaceCreate, PlaceUpdate
from app.services import artic_service
from app.services.project_service import get_project_or_404, check_and_complete_project

MAX_PLACES = 10


async def get_place_or_404(session: AsyncSession, project_id: int, place_id: int) -> Place:
    result = await session.execute(
        select(Place).where(Place.id == place_id, Place.project_id == project_id)
    )
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    return place


async def list_places(session: AsyncSession, project_id: int) -> list[Place]:
    await get_project_or_404(session, project_id)
    result = await session.execute(
        select(Place).where(Place.project_id == project_id)
    )
    return list(result.scalars().all())


async def get_place(session: AsyncSession, project_id: int, place_id: int) -> Place:
    await get_project_or_404(session, project_id)
    return await get_place_or_404(session, project_id, place_id)


async def add_place(session: AsyncSession, project_id: int, data: PlaceCreate) -> Place:
    project = await get_project_or_404(session, project_id)

    if len(project.places) >= MAX_PLACES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project cannot have more than {MAX_PLACES} places",
        )

    existing = await session.execute(
        select(Place).where(
            Place.project_id == project_id,
            Place.external_id == data.external_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Place with external_id {data.external_id} already exists in this project",
        )

    artwork = await artic_service.get_artwork(data.external_id)
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Artwork {data.external_id} not found in Art Institute API",
        )

    place = Place(project_id=project_id, external_id=data.external_id)
    session.add(place)
    await session.commit()
    await session.refresh(place)
    return place


async def update_place(
    session: AsyncSession, project_id: int, place_id: int, data: PlaceUpdate
) -> Place:
    project = await get_project_or_404(session, project_id)
    place = await get_place_or_404(session, project_id, place_id)

    if data.notes is not None:
        place.notes = data.notes
    if data.is_visited is not None:
        place.is_visited = data.is_visited

    await session.commit()
    await session.refresh(place)

    if data.is_visited:
        result = await session.execute(
            select(Project).where(Project.id == project_id).options(selectinload(Project.places))
        )
        refreshed_project = result.scalar_one()
        await check_and_complete_project(session, refreshed_project)

    return place
