from fastapi import APIRouter
from starlette import status

from app.routers.dependencies import UnitOfWorkDep, get_current_user, get_trading_bots_service
from app.schemas.trading_bots import TradingBotCreate

router = APIRouter(prefix="/trading-bots", tags=["Trading Bots"])


@router.post(
    '',
    name='Add Trading Bot',
    status_code=status.HTTP_201_CREATED,
)
async def create_trading_bot(
        data: TradingBotCreate,
        unit_of_work: UnitOfWorkDep,
        service: get_trading_bots_service,
        current_user: get_current_user
):
    return await service.create(unit_of_work, data, user_id=current_user.id)


@router.get(
    '',
    name='List Trading Bots',
    status_code=status.HTTP_200_OK,
)
async def list_trading_bots(
        unit_of_work: UnitOfWorkDep,
        service: get_trading_bots_service,
        current_user: get_current_user,
):
    return await service.list(unit_of_work, user_id=current_user.id)


@router.delete(
    '/{account_id}',
    name='Delete Trading Bot',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_trading_bot(
        account_id: int,
        unit_of_work: UnitOfWorkDep,
        service: get_trading_bots_service,
        current_user: get_current_user,
):
    return await service.delete(unit_of_work, account_id, user_id=current_user.id)
