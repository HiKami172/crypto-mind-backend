from sqlalchemy import Result, select
from sqlalchemy.orm import joinedload

from app.models import Message, Thread
from app.utils.repository import SQLAlchemyRepository


class ThreadRepository(SQLAlchemyRepository):
    model = Thread
    default_order_by = '-created_at'


    async def get_thread_messages_by_id(self, **whereclauses) -> Thread:
        statement = (
            select(self.model)
            .where(*self.get_where_clauses(**whereclauses))
            .options(joinedload(self.model.messages))
        )
        result: Result = await self.execute(statement)

        return await self.fetch_data(result.unique().scalar_one)


class MessageRepository(SQLAlchemyRepository):
    model = Message
    default_order_by = '-created_at'
