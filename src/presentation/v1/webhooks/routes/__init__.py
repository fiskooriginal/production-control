from fastapi import APIRouter

from src.presentation.v1.webhooks.routes import deliveries, subscriptions, test

router = APIRouter(tags=["webhooks"])

router.include_router(subscriptions.router, prefix="/webhooks")
router.include_router(deliveries.router, prefix="/webhooks")
router.include_router(test.router, prefix="/webhooks")
