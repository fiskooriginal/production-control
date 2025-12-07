from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def init_engine(db_url: str, *, echo: bool = False, pool_pre_ping: bool = True) -> AsyncEngine:
    return create_async_engine(
        db_url,
        echo=echo,
        pool_pre_ping=pool_pre_ping,
        future=True,
    )


async def dispose_engine(engine: AsyncEngine) -> None:
    await engine.dispose()


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)
