from fastapi import APIRouter

from src.api.v1.routers import healthcheck

router = APIRouter(prefix="/api/v1")

router.include_router(healthcheck.router)
