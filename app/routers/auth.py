from fastapi import APIRouter

from app.routers.dependencies import auth_backend, fastapi_users, google_oauth_client
from app.schemas import UserCreate, UserRead
from app.settings import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router.include_router(fastapi_users.get_verify_router(UserRead))
router.include_router(fastapi_users.get_reset_password_router())
router.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        settings.auth.key,
        redirect_url=settings.oauth.GOOGLE_REDIRECT_URI,
        is_verified_by_default=True
    ),
    prefix="/google"
)
