from typing import Any, AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import User, OAuthAccount
from app.settings import settings

engine = create_async_engine(settings.database.url, echo=settings.DEBUG)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

# TODO: Only for testing purposes, remove in production
engine_prod = create_async_engine(settings.database.url_prod, echo=settings.DEBUG)
async_session_prod = async_sessionmaker(bind=engine_prod, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


def get_prod_session() -> AsyncSession:  # TODO: Only for testing purposes, remove in production
    session_factory = async_session_prod if settings.DEBUG else async_session
    return session_factory()
