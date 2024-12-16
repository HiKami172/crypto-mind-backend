from pydantic import UUID4

from app.schemas.threads import ThreadMessagesByIdResponse, ThreadCreateRequest
from app.utils.unitofwork import IUnitOfWork
from app.models import Thread
from uuid import uuid4


class ThreadService:

    @staticmethod
    async def create(unit_of_work: IUnitOfWork, data: ThreadCreateRequest, user_id: int):
        """Create a new thread with the first message."""
        async with unit_of_work:
            new_thread = Thread(id=uuid4(), user_id=user_id, title=data.title)
            await unit_of_work.add(new_thread)
            await unit_of_work.commit()

            return new_thread

    @staticmethod
    async def retrieve(unit_of_work: IUnitOfWork, thread_id: UUID4):
        async with unit_of_work:
            return await unit_of_work.threads.get_thread_with_messages(pk=thread_id)

    @staticmethod
    async def list(unit_of_work: IUnitOfWork, page: int, per_page: int, **filter_by) -> dict:
        async with unit_of_work:
            return await unit_of_work.threads.list(page=page, per_page=per_page, **filter_by)

    @staticmethod
    async def list_messages(unit_of_work: IUnitOfWork, page: int, per_page: int, **filter_by) -> dict:
        async with unit_of_work:
            return await unit_of_work.messages.list(page=page, per_page=per_page, **filter_by)

    @staticmethod
    async def add_message(unit_of_work: IUnitOfWork, thread_id: UUID4, message):
        async with unit_of_work:
            await unit_of_work.messages.create(
                id=uuid4(),
                thread_id=thread_id,
                content=message["content"],
                role=message["role"]
            )

    @staticmethod
    async def get_messages(unit_of_work: IUnitOfWork, user_id: int, thread_id: str) -> ThreadMessagesByIdResponse:
        async with unit_of_work:
            thread = await unit_of_work.threads.get_thread_with_messages(pk=thread_id, user_id=user_id)
            return ThreadMessagesByIdResponse.model_validate(thread)
