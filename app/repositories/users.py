from sqlalchemy import Result

from app.models import User, BinanceAccount
from app.repositories import mixins
from app.utils.repository import SQLAlchemyRepository


class UserRepository(mixins.PaginateListMixins, SQLAlchemyRepository):
    model = User
    unique_rows = ('email',)

    async def get_by_email(self, email: str) -> User | None:
        result: Result = await super().retrieve(return_result=True, email=email)
        return result.scalar_one_or_none()


class BinanceAccountRepository(SQLAlchemyRepository):
    model = BinanceAccount
    unique_rows = ('id', )

