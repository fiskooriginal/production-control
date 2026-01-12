from fastapi import APIRouter

from src.presentation.v1.analytics import routes as analytics_routes
from src.presentation.v1.background_tasks import routes as background_tasks_routes
from src.presentation.v1.batches import routes as batches_routes
from src.presentation.v1.events import routes as events_routes
from src.presentation.v1.healthcheck import routes as healthcheck_routes
from src.presentation.v1.products import routes as products_routes
from src.presentation.v1.webhooks import routes as webhooks_routes
from src.presentation.v1.work_centers import routes as work_centers_routes

router = APIRouter(prefix="/api/v1")

router.include_router(analytics_routes.router)
router.include_router(background_tasks_routes.router)
router.include_router(batches_routes.router)
router.include_router(healthcheck_routes.router)
router.include_router(events_routes.router)
router.include_router(products_routes.router)
router.include_router(webhooks_routes.router)
router.include_router(work_centers_routes.router)
