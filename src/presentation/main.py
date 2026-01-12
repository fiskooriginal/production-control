from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import LOG_LEVEL
from src.core.database import dispose_engine, init_engine, make_session_factory
from src.core.logging import get_logger, setup_logging
from src.core.settings import CacheSettings, DatabaseSettings, MinIOSettings
from src.infrastructure.common.cache.redis import close_cache, init_cache
from src.infrastructure.common.storage.minio import init_minio_storage
from src.infrastructure.events.sync_service import EventTypeSyncService

setup_logging(LOG_LEVEL)
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")
    try:
        # Database
        db_settings = DatabaseSettings()
        logger.info(f"Database settings: {db_settings}")
        logger.info(f"Database URL: {db_settings.get_safe_url()}")
        engine = init_engine(db_settings.url)
        session_factory = make_session_factory(engine)
        app.state.engine = engine
        app.state.session_factory = session_factory

        # Event Types Sync
        async with session_factory() as session:
            sync_service = EventTypeSyncService(session)
            await sync_service.sync()

        # Cache
        cache_settings = CacheSettings()
        logger.info(f"Cache settings: {cache_settings}")
        cache_service, redis_pool = await init_cache(cache_settings)
        app.state.cache_service = cache_service
        app.state.redis_pool = redis_pool

        # Storage
        minio_settings = MinIOSettings()
        logger.info(f"Initializing MinIO storage: endpoint={minio_settings.endpoint}")
        storage_service = await init_minio_storage(minio_settings)
        app.state.storage_service = storage_service
        logger.info("MinIO storage initialized successfully")

        logger.info("Application started successfully")
    except Exception as e:
        logger.exception(f"Application startup failed: {e}")
        raise

    yield

    logger.info("Application shutdown initiated")
    try:
        await close_cache(redis_pool)
        await dispose_engine(engine)
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.exception(f"Application shutdown failed: {e}")
        raise


def add_routes(app: FastAPI) -> None:
    from src.presentation.v1 import router as v1_router

    app.include_router(v1_router)


def add_middlewares(app: FastAPI) -> None:
    from src.presentation.middlewares.logging import LoggingMiddleware

    app.add_middleware(LoggingMiddleware)


def add_exception_handlers(app: FastAPI) -> None:
    from src.presentation.exceptions.registry import register_exception_handlers

    register_exception_handlers(app)


app = FastAPI(title="Production Control API", lifespan=lifespan)

add_middlewares(app)
add_exception_handlers(app)
add_routes(app)
