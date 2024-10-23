from fastapi import APIRouter, status
from sqlalchemy import select

from app.settings import settings
from app.database import engine, engine_prod

router = APIRouter(prefix='/check', tags=['Checks'])


@router.get('/', status_code=status.HTTP_200_OK)
async def health_check():
    return {'status_code': 200, 'detail': 'ok', 'result': 'working', 'debug': settings.DEBUG}


@router.get('/database/', status_code=status.HTTP_200_OK, name='database check')
async def database_check():
    async with engine.connect() as conn:
        await conn.execute(select(1))

    async with engine_prod.connect() as conn:
        await conn.execute(select(1))

    return {'status_code': 200}
