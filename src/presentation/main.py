from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database import dispose_engine, init_engine, make_session_factory
from src.core.settings import DatabaseSettings
from src.presentation.api import register_exception_handlers
from src.presentation.api.routes import batches, products, work_centers


def add_routes(app: FastAPI) -> None:
    app.include_router(batches.router)
    app.include_router(products.router)
    app.include_router(work_centers.router)


def create_app(lifespan: Callable) -> FastAPI:
    app = FastAPI(title="Production Control API", lifespan=lifespan)

    register_exception_handlers(app)
    add_routes(app)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_settings = DatabaseSettings()
    engine = init_engine(db_settings.url)
    session_factory = make_session_factory(engine)
    app.state.engine = engine
    app.state.session_factory = session_factory

    yield

    await dispose_engine(engine)


app = create_app(lifespan)
