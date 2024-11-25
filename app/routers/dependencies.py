import uuid
from typing import Optional

from httpx_oauth.clients.google import GoogleOAuth2
from typing import Annotated
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy, BearerTransport,
)
from app.database import User, get_user_db
from app.settings import settings
from app.services import ThreadService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork

bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=settings.auth.key, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.auth.key
    verification_token_secret = settings.auth.key

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
get_current_user = Annotated[User, Depends(current_active_user)]

google_oauth_client = GoogleOAuth2(
    client_id=settings.oauth.GOOGLE_CLIENT_ID,
    client_secret=settings.oauth.GOOGLE_CLIENT_SECRET,
    scopes=["openid", "email", "profile"]
)


UnitOfWorkDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]


get_threads_service = Annotated[ThreadService, Depends(ThreadService)]



