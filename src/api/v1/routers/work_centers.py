from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.api.v1.schemas.work_centers import WorkCenterBaseSchema, WorkCenterCreateUpdateSchema, WorkCenterResponseSchema
from src.core.dependencies import DBSessionDI
from src.data.persistence.models import Batch, WorkCenter

router = APIRouter(prefix="/work_centers", tags=["work_centers"])


@router.get("", response_model=list[WorkCenterResponseSchema])
async def list_work_centers(session: DBSessionDI, skip: int = 0, limit: int = 100):
    stmt = (
        select(WorkCenter)
        .options(selectinload(WorkCenter.batches).selectinload(Batch.products))
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{uuid}", response_model=WorkCenterResponseSchema)
async def get_work_center(uuid: str, session: DBSessionDI):
    stmt = (
        select(WorkCenter)
        .where(WorkCenter.uuid == uuid)
        .options(selectinload(WorkCenter.batches).selectinload(Batch.products))
    )
    result = await session.execute(stmt)
    batch = result.scalar_one_or_none()

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WorkCenter не найден",
        )
    return batch


@router.post("", response_model=WorkCenterBaseSchema, status_code=status.HTTP_201_CREATED)
async def create_work_center(batch: WorkCenterCreateUpdateSchema, session: DBSessionDI):
    db_batch = WorkCenter(**batch.model_dump(exclude_none=True))
    session.add(db_batch)
    try:
        await session.commit()
        stmt = (
            select(WorkCenter)
            .where(WorkCenter.uuid == db_batch.uuid)
            .options(selectinload(WorkCenter.batches).selectinload(Batch.products))
        )
        db_batch = (await session.execute(stmt)).scalar_one()
    except IntegrityError as err:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания batch: {err!s}",
        ) from err
    return db_batch


@router.patch("/{uuid}", response_model=WorkCenterBaseSchema)
async def update_batch(uuid: str, upd: WorkCenterCreateUpdateSchema, session: DBSessionDI):
    update_body = upd.model_dump(exclude_none=True)
    if update_body.get("is_closed"):
        upd.closed_at = datetime.now()

    return (await session.execute(select(WorkCenter).where(WorkCenter.uuid == uuid))).scalar_one_or_none()
