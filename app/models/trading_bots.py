from uuid import UUID, uuid4

from sqlalchemy import Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from sqlalchemy.types import ARRAY

from app.models.base import Base


class TradingBot(Base):
    __tablename__ = 'trading_bot'

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4, index=True)
    binance_account_id: Mapped[UUID] = mapped_column(ForeignKey('binance_account.id'))
    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'), nullable=False)
    name = mapped_column(String, nullable=False)
    is_active = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    tickers = mapped_column(ARRAY(String), nullable=False, default=[])

    base_prompt = mapped_column(String, nullable=True)  # Use default base if not set
    additional_notes = mapped_column(String, nullable=True)  # Don't inject notes if not set
    risk_tolerance = mapped_column(Integer, nullable=False)
    target_profit = mapped_column(Integer, nullable=False)

    user = relationship("User", back_populates="bots")
    binance_account = relationship("BinanceAccount", back_populates="bots")
    activities = relationship("BotActivity", back_populates="bot", cascade="all, delete-orphan")


class BotActivity(Base):
    __tablename__ = 'bot_activity'

    id = mapped_column(Integer, primary_key=True, index=True)
    bot_id: Mapped[UUID] = mapped_column(ForeignKey('trading_bot.id'), nullable=False)
    timestamp = mapped_column(DateTime, default=datetime.utcnow)
    activity_type = mapped_column(String, nullable=False)  # E.g., "BUY", "SELL", "ANALYSIS"
    details = mapped_column(Text, nullable=True)  # Logs or additional details

    bot = relationship("TradingBot", back_populates="activities")
