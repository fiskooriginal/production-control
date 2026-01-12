from fastapi import APIRouter

from src.presentation.v1.batches.routes import aggregation, crud, import_export, products, reports

router = APIRouter(tags=["batches"])

router.include_router(crud.router, prefix="/batches")
router.include_router(products.router, prefix="/batches")
router.include_router(aggregation.router, prefix="/batches")
router.include_router(reports.router, prefix="/batches")
router.include_router(import_export.router, prefix="/batches")
