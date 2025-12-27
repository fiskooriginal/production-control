from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.presentation.api.dependencies import get_session

router = APIRouter(prefix="/healthcheck", tags=["healthcheck"])


@router.get("", status_code=status.HTTP_200_OK)
async def healthcheck() -> dict[str, str]:
    """
    Проверяет статус приложения.

    RESTful endpoint: GET /healthcheck
    """
    return {"status": "ok"}


@router.get("/database", status_code=status.HTTP_200_OK)
async def database_healthcheck(
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """
    Проверяет статус базы данных.

    RESTful endpoint: GET /healthcheck/database
    """
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
