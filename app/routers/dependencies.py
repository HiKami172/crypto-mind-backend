import uuid
from typing import Optional

from loguru import logger
from httpx import AsyncClient
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
from app.services import ThreadService, BinanceService, UserService, TradingBotService
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

    async def fetch_google_profile(self, access_token: str) -> dict:
        """Fetch user profile from Google using the access token."""
        async with AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                params={"alt": "json", "access_token": access_token},
            )
            response.raise_for_status()
            return response.json()

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        if user.oauth_accounts:
            oauth_account = user.oauth_accounts[0]
            if oauth_account.oauth_name == "google":
                try:
                    profile = await self.fetch_google_profile(oauth_account.access_token)
                    logger.info(f"Profile: {profile}")
                    update_dict = {
                        "full_name": profile.get("name", ""),
                        "avatar": profile.get("picture", ""),
                    }
                    await self.user_db.update(user, update_dict)
                except Exception as e:
                    print(f"Error fetching Google profile: {e}")

        logger.info(f"User {user.id} has registered.")

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
get_trading_bots_service = Annotated[TradingBotService, Depends(TradingBotService)]
get_users_service = Annotated[UserService, Depends(UserService)]



async def get_binance_service() -> BinanceService:
    service = BinanceService(
        api_key=settings.binance.BINANCE_API_KEY,
        api_secret=settings.binance.BINANCE_API_SECRET,
        testnet_api_key=settings.binance.TESTNET_BINANCE_API_KEY,
        testnet_api_secret=settings.binance.TESTNET_BINANCE_API_SECRET
    )
    await service.connect()
    try:
        yield service
    finally:
        await service.close()