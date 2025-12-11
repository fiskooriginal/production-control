from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from starlette import status

from src.core.dependencies import DBSessionDI

router = APIRouter(prefix="/healthchecks", tags=["healthchecks"])


@router.get("", status_code=status.HTTP_200_OK)
async def healthcheck():
    return {"status": "ok"}


@router.get("/postgres", status_code=status.HTTP_200_OK)
async def postgres(session: DBSessionDI):
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar_one()
        return {"status": "ok", "database": "connected"}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "database": "disconnected", "error": str(err)},
        ) from err
