from fastapi import APIRouter

from src.presentation.v1.webhooks.routes import deliveries, subscriptions, test

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

router.include_router(subscriptions.router)
router.include_router(deliveries.router)
router.include_router(test.router)
