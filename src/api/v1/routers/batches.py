from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.api.v1.schemas.batches import BatchBaseSchema, BatchCreateUpdateSchema, BatchResponseSchema
from src.core.dependencies import DBSessionDI
from src.data.persistence.models import Batch

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("", response_model=list[BatchResponseSchema])
async def list_batches(session: DBSessionDI, skip: int = 0, limit: int = 100):
    stmt = select(Batch).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{uuid}", response_model=BatchResponseSchema)
async def get_batch(uuid: str, session: DBSessionDI):
    stmt = (
        select(Batch).where(Batch.uuid == uuid).options(selectinload(Batch.work_center), selectinload(Batch.products))
    )
    result = await session.execute(stmt)
    batch = result.scalar_one_or_none()

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch не найден",
        )
    return batch


@router.post("", response_model=BatchBaseSchema, status_code=status.HTTP_201_CREATED)
async def create_batch(batch: BatchCreateUpdateSchema, session: DBSessionDI):
    db_batch = Batch(**batch.model_dump(exclude_none=True))
    session.add(db_batch)
    try:
        await session.commit()
        await session.refresh(db_batch)
    except IntegrityError as err:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания batch: {err!s}",
        ) from err
    except Exception as err:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания batch: {err!s}",
        ) from err
    return db_batch


@router.patch("/{uuid}", response_model=BatchBaseSchema)
async def update_batch(uuid: str, upd: BatchCreateUpdateSchema, session: DBSessionDI):
    update_body = upd.model_dump(exclude_none=True)
    if update_body.get("is_closed"):
        upd.closed_at = datetime.now()

    return (await session.execute(select(Batch).where(Batch.uuid == uuid))).scalar_one_or_none()
