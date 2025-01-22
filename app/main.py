from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from fastapi_healthz import (
    HealthCheckRegistry,
    HealthCheckDatabase, health_check_route,
)

from app.middlewares.context import RequestMiddleware
from app.settings import settings
from app.database import engine
from app.events import register_events
from app.routers import (
    threads,
    auth,
    users,
    binance, binance_accounts
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info('Start application')
    yield
    logger.info('Stop application')
    await engine.dispose()


def create_application() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title=settings.app_name,
        version=settings.version
    )
    register_events()
    _healthChecks = HealthCheckRegistry()
    db_sync_uri = settings.database.url.replace("+asyncpg", "")

    _healthChecks.add(HealthCheckDatabase(uri=db_sync_uri))

    app.include_router(users)
    app.include_router(auth)
    app.include_router(threads)
    app.include_router(binance)
    app.include_router(binance_accounts)
    app.add_api_route('/health', endpoint=health_check_route(registry=_healthChecks))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    app.add_middleware(RequestMiddleware)
    return app


app = create_application()
