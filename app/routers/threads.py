import datetime
from typing import Annotated

from fastapi import APIRouter, Query, status, HTTPException
from pydantic import UUID4, BaseModel
from sqlalchemy.sql.functions import user
from starlette.responses import JSONResponse

from app.routers.dependencies import UnitOfWorkDep, get_current_user, get_threads_service
from app.schemas.threads import ThreadCreateRequest, Thread, PaginatedMessagesResponse, MessageSchema
from app.inference.chat.model import ChatModel

router = APIRouter(prefix='/threads', tags=['Threads'])


@router.post(
    '/',
    name='Create Thread',
    description='Create new thread.',
    status_code=status.HTTP_201_CREATED,
)
async def create_thread(
        data: ThreadCreateRequest,
        unit_of_work: UnitOfWorkDep,
        service: get_threads_service,
        current_user: get_current_user
):
    return await service.create(unit_of_work, data, user_id=current_user.id)


@router.get(
    '/',
    # response_model=ThreadList,
    name='List Threads',
    description='Get all threads with pagination.',
    status_code=status.HTTP_200_OK,
)
async def get_threads(
        unit_of_work: UnitOfWorkDep,
        service: get_threads_service,
        current_user: get_current_user,
        page: Annotated[int | None, Query(ge=1)] = 1,
        per_page: Annotated[int | None, Query(ge=1, le=30)] = 10,
):
    result = await service.list(unit_of_work, user_id=current_user.id, page=page, per_page=per_page)
    result['items'] = {thread.id: thread for thread in result['items']}
    return result


@router.get(
    '/{thread_id}/',
    name='Retrieve Thread',
    description='Get certain thread.',
    status_code=status.HTTP_200_OK,
    response_model=Thread,
)
async def get_thread(thread_id: UUID4, unit_of_work: UnitOfWorkDep, service: get_threads_service):
    return await service.retrieve(unit_of_work, thread_id)


@router.delete(
    '/{thread_id}/',
    name='Delete Thread',
    description='Delete thread.',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_thread(
        user_id: int,
        unit_of_work: UnitOfWorkDep,
        service: get_threads_service,
        current_user: get_current_user,
):
    return await service.delete(unit_of_work, user_id, current_user_id=current_user.id)


@router.get(
    '/{thread_id}/messages/',
    status_code=status.HTTP_200_OK,
    description='Get paginated messages from specific thread.',
    name='List Messages',
    response_model=PaginatedMessagesResponse
)
async def get_messages(
        thread_id: str,
        unit_of_work: UnitOfWorkDep,
        service: get_threads_service,
        current_user: get_current_user,
        page: Annotated[int | None, Query(ge=1)] = 1,
        per_page: Annotated[int | None, Query(ge=1, le=30)] = 10,
):
    return await service.list_messages(unit_of_work, thread_id=thread_id, page=page, per_page=per_page)


class MessageRequest(BaseModel):
    message: str


@router.post(
    '/{thread_id}/messages/',
    name='Send Message',
    description='Send a message to specific thread.',
    status_code=status.HTTP_201_CREATED,
    # response_model=MessageSchema
)
async def send_message(
        thread_id: str,
        message_request: MessageRequest,
        unit_of_work: UnitOfWorkDep,
        service: get_threads_service,
        current_user: get_current_user,
):
    message = message_request.message
    thread = await service.retrieve(unit_of_work, thread_id)
    messages = [{"role": message.role, "content": message.content} for message in thread.messages]
    messages.append({"role": "user", "content": message})
    try:
        chat_model = ChatModel()
        model_response = chat_model.run(messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
    messages.append({"role": "assistant", "content": model_response})
    add_messages = [
        {"role": 'user', "content": message, "timestamp": datetime.datetime.utcnow().isoformat()},
        {"role": 'assistant', "content": model_response, "timestamp": datetime.datetime.utcnow().isoformat()},
    ]
    for message in add_messages:
        await service.add_message(unit_of_work, thread_id, message)
    return {"role": 'assistant', "content": model_response, "created_at": datetime.datetime.utcnow().isoformat()}
