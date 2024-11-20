from pydantic import UUID4

from app.schemas.threads import ThreadMessagesByIdResponse, ThreadRetrieveRequest, ThreadCreateRequest
from app.utils.conversions import alchemy_to_dict
from app.utils.unitofwork import IUnitOfWork
from app.models import Thread, Message
from uuid import uuid4


class ThreadService:

    async def create(self, unit_of_work: IUnitOfWork, data: ThreadCreateRequest, user_id: int, messages):
        """Create a new thread with the first message."""
        async with unit_of_work:
            new_thread = Thread(id=uuid4(), user_id=user_id, title=data.first_message)
            await unit_of_work.add(new_thread)
            for message in messages:
                new_message = Message(id=uuid4(), thread_id=new_thread.id, text=message['content'], role=message["role"])
                await unit_of_work.add(new_message)
            await unit_of_work.commit()

            return await unit_of_work.threads.get_thread_with_messages(pk=new_thread.id)

    async def retrieve(self, unit_of_work: IUnitOfWork, thread_id: UUID4):
        async with unit_of_work:
            return await unit_of_work.threads.get_thread_with_messages(pk=thread_id)

    async def list(self, unit_of_work: IUnitOfWork, page: int, per_page: int, **filter_by) -> dict:
        async with unit_of_work:
            return await unit_of_work.threads.list(page=page, per_page=per_page, **filter_by)

    async def add_message(self, unit_of_work: IUnitOfWork, thread_id: UUID4, message):
        async with unit_of_work:
            await unit_of_work.messages.create(id=uuid4(), thread_id=thread_id, text=message["content"], role=message["role"])

    async def get_messages(self, unit_of_work: IUnitOfWork, user_id: int, thread_id: str) -> ThreadMessagesByIdResponse:
        async with unit_of_work:
            thread = await unit_of_work.threads.get_thread_with_messages(pk=thread_id, user_id=user_id)
            return ThreadMessagesByIdResponse.model_validate(thread)
