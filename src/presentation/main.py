from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import LOG_LEVEL
from src.core.database import dispose_engine, init_engine, make_session_factory
from src.core.logging import get_logger, setup_logging
from src.core.settings import DatabaseSettings
from src.presentation.api import register_exception_handlers
from src.presentation.api.middleware import LoggingMiddleware
from src.presentation.api.routes import batches, products, work_centers

setup_logging(LOG_LEVEL)
logger = get_logger("app")


def add_routes(app: FastAPI) -> None:
    app.include_router(batches.router)
    app.include_router(products.router)
    app.include_router(work_centers.router)


def create_app(lifespan: Callable) -> FastAPI:
    app = FastAPI(title="Production Control API", lifespan=lifespan)

    app.add_middleware(LoggingMiddleware)
    register_exception_handlers(app)
    add_routes(app)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")
    try:
        db_settings = DatabaseSettings()
        engine = init_engine(db_settings.url)
        session_factory = make_session_factory(engine)
        app.state.engine = engine
        app.state.session_factory = session_factory
        logger.info("Application started successfully")
    except Exception as e:
        logger.exception(f"Application startup failed: {e}")
        raise

    yield

    logger.info("Application shutdown initiated")
    try:
        await dispose_engine(engine)
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.exception(f"Application shutdown failed: {e}")
        raise


app = create_app(lifespan)
