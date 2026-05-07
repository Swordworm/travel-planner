from fastapi import APIRouter

from app.api.v1.routers import projects, places

router = APIRouter(prefix="/api/v1")
router.include_router(projects.router)
router.include_router(places.router)
