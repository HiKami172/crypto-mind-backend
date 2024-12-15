from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.middlewares.context import RequestMiddleware
from app.settings import settings
from app.database import engine
from app.events import register_events
from app.routers import (
    health_check,
    threads,
    auth,
    users,
    binance
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info('Start application')
    yield
    logger.info('Stop application')
    await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    register_events()

    app.include_router(users)
    app.include_router(auth)
    app.include_router(health_check)
    app.include_router(threads)
    app.include_router(binance)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(RequestMiddleware)
    return app


app = create_application()
