from fastapi import HTTPException

from app.schemas.binance import AddBinanceAccountRequest
from app.utils.unitofwork import IUnitOfWork


class UserService:

    @staticmethod
    async def add_binance_account(unit_of_work: IUnitOfWork, data: AddBinanceAccountRequest, user_id: str):
        binance_account = data.model_dump()
        async with unit_of_work:
            return await unit_of_work.binance_accounts.create(user_id=user_id, **binance_account)

    @staticmethod
    async def list_binance_accounts(unit_of_work: IUnitOfWork, user_id: str):
        async with unit_of_work:
            return await unit_of_work.binance_accounts.list(user_id=user_id)

    @staticmethod
    async def delete_binance_account(unit_of_work: IUnitOfWork, account_id: str, user_id: str):
        async with unit_of_work:
            account = await unit_of_work.binance_accounts.retrieve(pk=account_id)
            if account.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access Denied.")
            return await unit_of_work.binance_accounts.delete(pk=account_id)
