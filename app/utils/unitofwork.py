from abc import ABC, abstractmethod

from loguru import logger

from app.database import async_session
from app.repositories import (
    MessageRepository,
    ThreadRepository,
    UserRepository,
    BinanceAccountRepository,
    TradingBotRepository
)


class IUnitOfWork(ABC):
    users: UserRepository
    binance_accounts: BinanceAccountRepository
    trading_bots: TradingBotRepository
    threads: ThreadRepository
    messages: MessageRepository

    @abstractmethod
    def __init__(self):
        raise NotImplemented

    @abstractmethod
    async def __aenter__(self):
        raise NotImplemented

    @abstractmethod
    async def __aexit__(self, *args):
        raise NotImplemented

    @abstractmethod
    async def commit(self):
        raise NotImplemented

    @abstractmethod
    async def add(self, instance):
        raise NotImplemented

    @abstractmethod
    async def rollback(self):
        raise NotImplemented


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory=None):
        session_factory = session_factory or async_session
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.threads = ThreadRepository(self.session)
        self.messages = MessageRepository(self.session)
        self.binance_accounts = BinanceAccountRepository(self.session)
        self.trading_bots = TradingBotRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            logger.exception(
                "An error occurred while processing the request. Rolling back. Error: {exc}", exc=exc, exc_info=exc
            )
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()
        await logger.complete()

        if exc:
            raise exc

    async def commit(self):
        await self.session.commit()

    async def add(self, instance):
        self.session.add(instance)

    async def rollback(self):
        await self.session.rollback()
