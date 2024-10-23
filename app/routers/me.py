from fastapi import APIRouter

from app.routers.dependencies import UnitOfWorkDep, get_current_user_id, get_user_service
from app.schemas.users import UserList

router = APIRouter(prefix='/me')


@router.get(
    '/',
    response_model=UserList,
    tags=['Auth'],
    description='Get information about current user.',
    name='Me',
)
async def me(
    current_user_id: get_current_user_id,
    unit_of_work: UnitOfWorkDep,
    user_service: get_user_service,
):
    return await user_service.retrieve(unit_of_work, current_user_id)
