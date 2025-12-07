from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import v1
from src.core.database import dispose_engine, init_engine, make_session_factory
from src.core.settings import DatabaseSettings


def create_app(lifespan: Callable) -> FastAPI:
    return FastAPI(title="Production Control API", lifespan=lifespan)


def include_routers(app: FastAPI):
    app.include_router(v1.router)


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
include_routers(app)
