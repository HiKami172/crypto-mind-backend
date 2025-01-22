from typing import List, Optional
from pydantic import BaseModel, Field, UUID4


class TradingBotBase(BaseModel):
    name: str
    is_active: bool
    binance_account_id: UUID4
    user_id: UUID4
    tickers: List[str] = Field(default_factory=list, description="List of tickers to trade on.")
    base_prompt: Optional[str] = Field(default=None, description="Notes and remarks for LLM to use.")
    additional_notes: Optional[str] = Field(default=None, description="Notes and remarks for LLM to use.")
    risk_tolerance: int = Field(..., ge=0, le=100, description="Risk tolerance from 0 to 100.")
    target_profit: int = Field(..., ge=0, le=100, description="Target profit percentage from 0 to 100.")


class TradingBotCreate(TradingBotBase):
    pass


class TradingBotRead(TradingBotBase):
    id: UUID4


class TradingBotList(TradingBotBase):
    pass


class TradingBotUpdate(TradingBotBase):
    pass
