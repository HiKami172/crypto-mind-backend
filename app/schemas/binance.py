from pydantic import BaseModel

from app.models.users import BinanceAccountType


class AddBinanceAccountRequest(BaseModel):
    name: str
    api_key: str
    secret_key: str
    account_type: BinanceAccountType


