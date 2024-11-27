from sqlalchemy import Result, select
from sqlalchemy.orm import joinedload

from app.models import Message, Thread
from app.repositories import mixins
from app.utils.repository import SQLAlchemyRepository


class ThreadRepository(mixins.PaginateListMixins, SQLAlchemyRepository):
    model = Thread
    default_order_by = '-updated_at'

    async def get_thread_with_messages(self, **whereclauses) -> Thread:
        statement = (
            select(self.model)
            .where(*self.get_where_clauses(**whereclauses))
            .options(joinedload(self.model.messages))
        )
        result: Result = await self.execute(statement)

        return await self.fetch_data(result.unique().scalar_one)


class MessageRepository(mixins.PaginateListMixins, SQLAlchemyRepository):
    model = Message
    default_order_by = '-created_at'

    async def list(self, *, page: int | None = 1, per_page: int | None = 10, **filter_by) -> dict:
        return await super().list(page=page, per_page=per_page, is_reversed=True, **filter_by)
