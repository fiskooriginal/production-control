from fastapi import APIRouter, status
from sqlalchemy import text

from src.presentation.di.common import async_session

router = APIRouter(prefix="/api/healthcheck", tags=["healthcheck"])


@router.get("/service", status_code=status.HTTP_200_OK)
async def healthcheck() -> dict[str, str]:
    """
    Проверяет статус приложения.
    """
    return {"status": "ok"}


@router.get("/database", status_code=status.HTTP_200_OK)
async def database_healthcheck(session: async_session) -> dict[str, str]:
    """
    Проверяет статус базы данных.
    """
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
