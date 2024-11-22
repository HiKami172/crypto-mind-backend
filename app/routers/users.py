from fastapi import APIRouter

from app.schemas import UserRead, UserUpdate
from app.routers.dependencies import fastapi_users

router = APIRouter(prefix="/users", tags=["Users"])
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
