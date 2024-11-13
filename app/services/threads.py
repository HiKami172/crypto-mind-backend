from pydantic import UUID4

from app.schemas.threads import ThreadMessagesByIdResponse, ThreadRetrieveRequest, ThreadCreateRequest
from app.utils.unitofwork import IUnitOfWork
from app.models import Thread, Message
from uuid import uuid4


class ThreadService:

    async def retrieve(self, unit_of_work: IUnitOfWork, thread_id: UUID4) -> Thread:
        async with unit_of_work:
            return await unit_of_work.threads.retrieve(pk=thread_id)

    async def list(self, unit_of_work: IUnitOfWork, page: int, per_page: int, **filter_by) -> dict:
        async with unit_of_work:
            return await unit_of_work.threads.list(page=page, per_page=per_page, **filter_by)

    async def get_thread_messages_by_id(self, unit_of_work: IUnitOfWork, user_id: int,
                                        thread_id: str) -> ThreadMessagesByIdResponse:
        async with unit_of_work:
            thread = await unit_of_work.threads.get_thread_messages_by_id(pk=thread_id, user_id=user_id)
            return ThreadMessagesByIdResponse.model_validate(thread)

    async def create(self, unit_of_work: IUnitOfWork, data: ThreadCreateRequest) -> ThreadRetrieveRequest:
        """Create a new thread with the first message."""
        async with unit_of_work:
            new_thread = Thread(id=uuid4(), user_id=data.user_id, title="New Thread")
            await unit_of_work.add(new_thread)

            new_message = Message(id=uuid4(), thread_id=new_thread.id, text=data.first_message, role='user')
            await unit_of_work.add(new_message)

            await unit_of_work.commit()

            return ThreadRetrieveRequest(id=new_thread.id)
