import datetime
from typing import Annotated

from fastapi import APIRouter, Query, status, HTTPException
from pydantic import UUID4, BaseModel
from sqlalchemy.sql.functions import user
from starlette.responses import JSONResponse

from app.routers.dependencies import UnitOfWorkDep, get_current_user, get_threads_service, get_user_service
from app.schemas.threads import ThreadList, ThreadCreateRequest, ThreadCreateResponse, Thread
from app.inference.chat.model import ChatModel

router = APIRouter(prefix='/threads', tags=['Threads'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    description='Create new thread.',
    name='Create Thread',
)
async def create_thread(
    data: ThreadCreateRequest,
    unit_of_work: UnitOfWorkDep,
    service: get_threads_service,
    current_user: get_current_user
):
    try:
        chat_model = ChatModel()
        model_response = chat_model.run([{"role": "user", "content": data.first_message}])
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

    messages =[
        {"role": 'user', "content": data.first_message, "timestamp": datetime.datetime.utcnow().isoformat()},
        {"role": 'assistant', "content": model_response, "timestamp": datetime.datetime.utcnow().isoformat()},
    ]
    thread = await service.create(unit_of_work, data, user_id=current_user.id, messages=messages)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": str(thread.id),
            "title": thread.title,
            "createdAt": thread.created_at.isoformat(),
            "messages": [
                {
                    "role": message.role,
                    "content": message.text,
                }
                for message in thread.messages
            ]
        },
    )


@router.get(
    '/',
    # response_model=ThreadList,
    status_code=status.HTTP_200_OK,
    description='Get all threads with pagination.',
    name='List Threads',
)
async def get_threads(
    unit_of_work: UnitOfWorkDep,
    service: get_threads_service,
    current_user: get_current_user,
    page: Annotated[int | None, Query(ge=1)] = 1,
    per_page: Annotated[int | None, Query(ge=1, le=30)] = 10,
):
    result = await service.list(unit_of_work, user_id=current_user.id, page=page, per_page=per_page)
    return result["items"]


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
    current_user: get_current_user,
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
        current_user: get_current_user,
):
    thread = await service.retrieve(unit_of_work, thread_id)
    return JSONResponse(
        content={
            "messages": [
                {
                    "role": message.role,
                    "content": message.text,
                }
                for message in thread.messages
            ]
        }
    )


class MessageRequest(BaseModel):
    message: str

@router.post(
    '/{thread_id}/messages/',
    status_code=status.HTTP_201_CREATED,
    description='Send a message to specific thread.',
    name='Send Message',
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
    messages = [{"role": message.role, "content": message.text} for message in thread.messages]
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
    return JSONResponse(
        content={
            "messages": [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in messages
            ]
        }
    )