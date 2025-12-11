from fastapi import APIRouter

from src.api.v1.routers import batches, healthchecks, products, work_centers

router = APIRouter(prefix="/v1")

router.include_router(healthchecks.router)
router.include_router(batches.router)
router.include_router(work_centers.router)
router.include_router(products.router)
