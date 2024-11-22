from typing import Annotated

from fastapi import APIRouter, Query, status
from pydantic import UUID4

from app.routers.dependencies import UnitOfWorkDep, current_active_user, get_threads_service
from app.schemas.threads import ThreadList, ThreadCreateRequest, ThreadCreateResponse, Thread

router = APIRouter(prefix='/threads', tags=['Threads'])


@router.post(
    '/',
    response_model=ThreadCreateResponse,
    status_code=status.HTTP_201_CREATED,
    description='Create new thread.',
    name='Create Thread',
)
async def create_thread(data: ThreadCreateRequest, unit_of_work: UnitOfWorkDep, service: get_threads_service):
    return await service.create(unit_of_work, data)


@router.get(
    '/',
    response_model=ThreadList,
    status_code=status.HTTP_200_OK,
    description='Get all threads with pagination.',
    name='List Threads',
)
async def get_threads(
    unit_of_work: UnitOfWorkDep,
    service: get_threads_service,
    current_user: current_active_user,
    page: Annotated[int | None, Query(ge=1)] = 1,
    per_page: Annotated[int | None, Query(ge=1, le=30)] = 10,
):
    return await service.list(unit_of_work, user_id=current_user.id, page=page, per_page=per_page)


@router.get(
    '/{thread_id}/',
    response_model=Thread,
    status_code=status.HTTP_200_OK,
    description='Get certain thread.',
    name='Retrieve Thread',
)
async def get_thread(thread_id: UUID4, unit_of_work: UnitOfWorkDep, service: get_threads_service):
    return await service.retrieve(unit_of_work, thread_id)


@router.delete(
    '/{thread_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Delete thread.',
    name='Delete Thread',
)
async def delete_thread(
    user_id: int,
    unit_of_work: UnitOfWorkDep,
    service: get_threads_service,
    current_user: current_active_user,
):
    return await service.delete(unit_of_work, user_id, current_user_id=current_user.id)


# Messages

@router.get(
    '/{thread_id}/messages',
    status_code=status.HTTP_200_OK,
    description='Get paginated messages from specific thread.',
    name='List Messages'
)
async def get_messages(
        thread_id: str,
        unit_of_work: UnitOfWorkDep,
        service: get_threads_service,
        current_user: current_active_user,
):
    return await service.get_messages(unit_of_work, thread_id, current_user.id)


@router.post(
    '/{thread_id}/messages/',
    status_code=status.HTTP_201_CREATED,
    description='Send a message to specific thread.',
    name='Send Message',
)
async def send_message(
        thread_id: str,
        message: str,
        unit_of_work: UnitOfWorkDep,
        service: get_threads_service,
        current_user: current_active_user,
):
    return await service.send_message(unit_of_work, thread_id, message, current_user.id)