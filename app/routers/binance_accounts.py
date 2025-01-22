from fastapi import APIRouter
from starlette import status

from app.routers.dependencies import UnitOfWorkDep, get_current_user, get_users_service
from app.schemas.binance import AddBinanceAccountRequest

router = APIRouter(prefix="/binance/accounts", tags=["Binance"])


@router.post(
    '',
    name='Add Binance Account',
    description='Add Binance account credentials.',
    status_code=status.HTTP_201_CREATED,
)
async def create_binance_account(
        data: AddBinanceAccountRequest,
        unit_of_work: UnitOfWorkDep,
        service: get_users_service,
        current_user: get_current_user
):
    return await service.add_binance_account(unit_of_work, data, user_id=current_user.id)


@router.get(
    '',
    name='List Accounts',
    description='List Binance accounts\' details',
    status_code=status.HTTP_200_OK,
)
async def list_binance_accounts(
        unit_of_work: UnitOfWorkDep,
        service: get_users_service,
        current_user: get_current_user,
):
    return await service.list_binance_accounts(unit_of_work, user_id=current_user.id)


@router.delete(
    '/{account_id}',
    name='Delete Account',
    description='Delete Binance account record.',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_binance_account(
        account_id: int,
        unit_of_work: UnitOfWorkDep,
        service: get_users_service,
        current_user: get_current_user,
):
    return await service.delete_binance_account(unit_of_work, account_id, user_id=current_user.id)
