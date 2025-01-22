from app.models import TradingBot
from app.repositories import mixins
from app.utils.repository import SQLAlchemyRepository


class TradingBotRepository(mixins.PaginateListMixins, SQLAlchemyRepository):
    model = TradingBot
    default_order_by = '-updated_at'

