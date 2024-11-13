from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.routers.dependencies import UnitOfWorkDep, get_current_user, get_user_service
from app.schemas.users import UserBase

router = APIRouter(prefix='/me')


@router.get(
    '/',
    response_model=UserBase,
    tags=['Auth'],
    description='Get information about current user.',
    name='Me',
)
async def me(
    current_user: get_current_user,
    unit_of_work: UnitOfWorkDep,
    user_service: get_user_service,
):
    result = await user_service.retrieve(unit_of_work, current_user.id)
    return JSONResponse(result)
