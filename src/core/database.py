from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.core.logging import get_logger

logger = get_logger("database")


def init_engine(db_url: str, *, echo: bool = False, pool_pre_ping: bool = True) -> AsyncEngine:
    engine = create_async_engine(
        db_url,
        echo=echo,
        pool_pre_ping=pool_pre_ping,
        future=True,
    )

    _setup_engine_logging(engine)
    logger.info("Database engine initialized.")

    return engine


def _setup_engine_logging(engine: AsyncEngine) -> None:
    """Настраивает логирование событий SQLAlchemy"""

    @event.listens_for(engine.sync_engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        logger.debug("Database connection established")

    @event.listens_for(engine.sync_engine, "close")
    def receive_close(dbapi_conn, connection_record):
        logger.debug("Database connection closed")

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        logger.debug(f"SQL: {statement[:200]}")

    @event.listens_for(engine.sync_engine, "handle_error")
    def receive_handle_error(exception_context):
        logger.exception(f"Database error: {exception_context.original_exception}")


async def dispose_engine(engine: AsyncEngine) -> None:
    logger.info("Disposing database engine")
    await engine.dispose()
    logger.info("Database engine disposed")


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)
