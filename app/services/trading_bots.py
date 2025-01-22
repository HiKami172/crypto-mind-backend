from pydantic import UUID4

from app.schemas.trading_bots import TradingBotCreate
from app.utils.unitofwork import IUnitOfWork


class TradingBotService:

    @staticmethod
    async def create(unit_of_work: IUnitOfWork, data: TradingBotCreate, user_id: UUID4):
        """Create a new thread with the first message."""
        model_dict = data.model_dump()
        async with unit_of_work:
            return await unit_of_work.trading_bots.create(user_id=user_id, **model_dict)

    @staticmethod
    async def retrieve(unit_of_work: IUnitOfWork, trading_bot_id: UUID4):
        async with unit_of_work:
            return await unit_of_work.trading_bots.retrieve(pk=trading_bot_id)

    @staticmethod
    async def list(unit_of_work: IUnitOfWork, page: int, per_page: int, **filter_by):
        async with unit_of_work:
            return await unit_of_work.trading_bots.list(page=page, per_page=per_page, **filter_by)

    @staticmethod
    async def update(unit_of_work: IUnitOfWork, data):
        model_dict = data.model_dump()
        async with unit_of_work:
            return await unit_of_work.trading_bots.update(model_dict)

    @staticmethod
    async def delete(unit_of_work: IUnitOfWork, trading_bot_id: UUID4):
        async with unit_of_work:
            return await unit_of_work.trading_bots.delete(pk=trading_bot_id)