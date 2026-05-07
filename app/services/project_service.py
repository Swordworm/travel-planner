from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.project import Project
from app.models.place import Place
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services import artic_service


async def get_project_or_404(session: AsyncSession, project_id: int) -> Project:
    result = await session.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.places))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


async def list_projects(session: AsyncSession) -> list[Project]:
    result = await session.execute(
        select(Project).options(selectinload(Project.places))
    )
    return list(result.scalars().all())


async def get_project(session: AsyncSession, project_id: int) -> Project:
    return await get_project_or_404(session, project_id)


async def create_project(session: AsyncSession, data: ProjectCreate) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    session.add(project)
    await session.flush()

    if data.places:
        if len(data.places) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project cannot have more than 10 places",
            )
        seen = set()
        for place_data in data.places:
            if place_data.external_id in seen:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Duplicate external_id: {place_data.external_id}",
                )
            seen.add(place_data.external_id)

            artwork = await artic_service.get_artwork(place_data.external_id)
            if not artwork:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Artwork {place_data.external_id} not found in Art Institute API",
                )
            session.add(Place(project_id=project.id, external_id=place_data.external_id))

    await session.commit()
    await session.refresh(project)
    result = await session.execute(
        select(Project).where(Project.id == project.id).options(selectinload(Project.places))
    )
    return result.scalar_one()


async def update_project(session: AsyncSession, project_id: int, data: ProjectUpdate) -> Project:
    project = await get_project_or_404(session, project_id)

    if any(p.is_visited for p in project.places):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update project with visited places",
        )

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.start_date is not None:
        project.start_date = data.start_date

    await session.commit()
    await session.refresh(project)
    return project


async def delete_project(session: AsyncSession, project_id: int) -> None:
    project = await get_project_or_404(session, project_id)

    if any(p.is_visited for p in project.places):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete project with visited places",
        )

    await session.delete(project)
    await session.commit()


async def check_and_complete_project(session: AsyncSession, project: Project) -> None:
    if project.places and all(p.is_visited for p in project.places):
        project.is_completed = True
        await session.commit()
