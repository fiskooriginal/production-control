from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.api.v1.schemas.products import ProductCreateUpdateSchema, ProductResponseSchema
from src.core.dependencies import DBSessionDI
from src.data.persistence.models import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponseSchema])
async def list_batches(session: DBSessionDI, skip: int = 0, limit: int = 100):
    stmt = select(Product).options(selectinload(Product.batch)).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{uuid}", response_model=ProductResponseSchema)
async def get_batch(uuid: str, session: DBSessionDI):
    stmt = (
        select(Product)
        .where(Product.uuid == uuid)
        .options(selectinload(Product.work_center), selectinload(Product.products))
    )
    result = await session.execute(stmt)
    batch = result.scalar_one_or_none()

    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product не найден",
        )
    return batch


@router.post("", response_model=ProductResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_batch(batch: ProductCreateUpdateSchema, session: DBSessionDI):
    db_batch = Product(**batch.model_dump(exclude_none=True))
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
    return db_batch


@router.patch("/{uuid}", response_model=ProductResponseSchema)
async def update_batch(uuid: str, upd: ProductCreateUpdateSchema, session: DBSessionDI):
    update_body = upd.model_dump(exclude_none=True)
    if update_body.get("is_closed"):
        upd.closed_at = datetime.now()

    return (await session.execute(select(Product).where(Product.uuid == uuid))).scalar_one_or_none()
