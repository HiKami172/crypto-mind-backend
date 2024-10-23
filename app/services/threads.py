from app.schemas.threads import FilterQuery, ThreadList, ThreadMessagesByIdResponse
from app.utils.unitofwork import IUnitOfWork


class ThreadService:

    async def retrieve(self, unit_of_work: IUnitOfWork, user_id: int, filter_query: FilterQuery) -> ThreadList:
        data = filter_query.model_dump()
        data['user_id'] = user_id

        async with unit_of_work:
            threads = await unit_of_work.threads.list_with_tags(**data)
            return ThreadList(threads=threads)

    async def get_thread_messages_by_id(self, unit_of_work: IUnitOfWork, user_id: int, thread_id: str) -> ThreadMessagesByIdResponse:
        async with unit_of_work:
            thread = await unit_of_work.threads.get_thread_messages_by_id(pk=thread_id, user_id=user_id)
            return ThreadMessagesByIdResponse.model_validate(thread)
