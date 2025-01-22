from typing import Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, SQLAlchemyBaseOAuthAccountTableUUID
from uuid import UUID, uuid4

from sqlalchemy import String, Enum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum

from app.models.base import Base


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class BinanceAccountType(PyEnum):
    TESTNET = "testnet"
    LIVE = "live"


class BinanceAccount(Base):
    __tablename__ = 'binance_account'

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'), nullable=False)
    name = mapped_column(String, nullable=False)
    api_key = mapped_column(String, nullable=False)
    secret_key = mapped_column(String, nullable=False)
    account_type = mapped_column(Enum(BinanceAccountType), nullable=False)
    is_active = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="binance_accounts")
    bots = relationship("TradingBot", back_populates="binance_account")


class User(SQLAlchemyBaseUserTableUUID, Base):
    full_name: Mapped[str] = mapped_column(String(50), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship("OAuthAccount", lazy="joined")
    binance_accounts: Mapped[list[BinanceAccount]] = relationship(back_populates='user')
    threads: Mapped[list['Thread']] = relationship(back_populates='user')
    bots: Mapped[list['TradingBot']] = relationship(back_populates='user')
