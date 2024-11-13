from typing import Annotated

from fastapi import APIRouter, Query, status

from app.routers.dependencies import UnitOfWorkDep, get_current_user, get_user_service
from app.schemas.users import UserList, UserPartialUpdate, UserSignUp, UserUpdate

router = APIRouter(prefix='/users', tags=['Users'])


@router.post(
    '/',
    response_model=UserList,
    status_code=status.HTTP_201_CREATED,
    description='Create new user.',
    name='Create',
)
async def create_user(data: UserSignUp, unit_of_work: UnitOfWorkDep, service: get_user_service):
    return await service.create(unit_of_work, data)


@router.get(
    '/',
    response_model=UserList,
    status_code=status.HTTP_200_OK,
    description='Get all users with pagination.',
    name='List',
)
async def get_users(
    unit_of_work: UnitOfWorkDep,
    service: get_user_service,
    page: Annotated[int | None, Query(ge=1)] = 1,
    per_page: Annotated[int | None, Query(ge=1, le=30)] = 10,
):
    return await service.list(unit_of_work, page=page, per_page=per_page)


@router.get(
    '/{user_id}/',
    response_model=UserList,
    status_code=status.HTTP_200_OK,
    description='Get certain user.',
    name='Retrieve',
)
async def get_user(user_id: int, unit_of_work: UnitOfWorkDep, service: get_user_service):
    return await service.retrieve(unit_of_work, user_id)


@router.put(
    '/{user_id}/',
    response_model=UserList,
    status_code=status.HTTP_200_OK,
    description='Update the user.',
    name='Update',
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    unit_of_work: UnitOfWorkDep,
    service: get_user_service,
    current_user: get_current_user,
):
    return await service.update(unit_of_work, user_id, data, current_user_id=current_user.id)


@router.patch(
    '/{user_id}/',
    response_model=UserList,
    status_code=status.HTTP_200_OK,
    description='Partial update the user.',
    name='Partial update',
)
async def partial_update_user(
    user_id: int,
    data: UserPartialUpdate,
    unit_of_work: UnitOfWorkDep,
    service: get_user_service,
    current_user: get_current_user,
):
    return await service.partial_update(unit_of_work, user_id, data, current_user_id=current_user.id)


@router.delete(
    '/{user_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    description='Disable account.',
    name='Disable',
)
async def delete_user(
    user_id: int,
    unit_of_work: UnitOfWorkDep,
    service: get_user_service,
    current_user: get_current_user,
):
    return await service.delete(unit_of_work, user_id, current_user_id=current_user.id)
