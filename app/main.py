from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from app.settings import settings
from app.database import engine
from app.routers import users, auth, health_check, me, threads


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info('Start application')
    yield
    logger.info('Stop application')
    await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(users)
    app.include_router(auth)
    app.include_router(health_check)
    app.include_router(me)
    app.include_router(threads)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    return app


app = create_application()
