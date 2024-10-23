from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, WebSocket
from fastapi.security import APIKeyQuery, HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_403_FORBIDDEN
from typing_extensions import Annotated

from app.settings import settings
from app.database import async_session
from app.exceptions.auth_exceptions import (
    IncorrectEmailOrPassException,
    InvalidTokenSignatureException,
    TokenExpireException,
)
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.auth import AuthServiceSchema, Token, TokenData, TokenSchema
from app.schemas.users import UserSignIn
from app.utils.password import verify_password

http_bearer = HTTPBearer()


class WebsocketAPIKeyQuery(APIKeyQuery):
    async def __call__(self, websocket: WebSocket) -> str | None:
        api_key = websocket.query_params.get(self.model.name)
        if not api_key:
            if self.auto_error:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
            else:
                return None

        return api_key


query_token = WebsocketAPIKeyQuery(name='token')


class AuthService:
    async def get_user(self, user_email: str) -> User:
        '''
        Get user with email=user_email`.
        :param user_email: User's email
        :return: User
        :raises:
                Raise error if user's account is disabled.
                Raise error if user not found and create_if_not_exist=False
        '''

        async with async_session() as session:
            users_repo = UserRepository(session)
            user = await users_repo.get_by_email(email=user_email)

            if user:
                return user

            raise IncorrectEmailOrPassException

    async def signin(self, user_in: UserSignIn) -> TokenSchema:
        '''
        Sign in user.
        Set token to redis and return that.
        :param user_in: UserSignIn
        :return: TokenSchema
        :raises:
                Raise error if exist user has no password (happens if user created from email though token)
                Raise error if password invalid

        '''
        user = await self.get_user(user_email=user_in.email)

        if verify_password(user_in.password, user.password):
            token = TokenSchema(access_token=self.create_token(user_email=user_in.email, token_type='access'))
            if user_in.keep_logged_in:
                token.refresh_token = self.create_token(user_email=user_in.email, token_type='refresh')

            return token

        raise IncorrectEmailOrPassException()

    async def verify(self, token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]) -> int:
        '''
        Check Bearer token.
        :param token: HTTPAuthorizationCredentials
        :return: user.id
        '''
        token = token.credentials

        token_data = self.check_token(token)
        user = await self.get_user(user_email=token_data.user_email)
        return user.id

    async def verify_from_query(self, token: Annotated[str, Depends(query_token)]) -> int:
        '''
        Check token provided in query.
        :param token: HTTPAuthorizationCredentials
        :return: user.id
        '''
        token_data = self.check_token(token)
        user = await self.get_user(user_email=token_data.user_email)
        return user.id

    async def refresh_token(self, refresh_token: str) -> Token:
        '''
        Refresh token.
        :param refresh_token: str
        :return: Token
        '''
        try:
            token_data = self.check_token(token=refresh_token)
            return self.create_token(user_email=token_data.user_email)
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpireException
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenSignatureException

    def check_token(self, token: str) -> TokenData:
        '''
        Check token in all services.
        :param token: User's token
        :return: TokenData
        :raises:
                Raise error if token expired
        '''
        auth_schema = AuthServiceSchema(**settings.auth.model_dump(exclude=['access_expire', 'refresh_expire']))
        try:
            token_data = jwt.decode(token, **auth_schema.model_dump(exclude_unset=True))
            return TokenData(**token_data)
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpireException
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenSignatureException

    @staticmethod
    def create_token(user_email: str, token_type: str = 'access') -> Token:
        '''
        Obtain new token.
        :param user_email: User's email
        :param token_type: Token type
        :return: TokenSchema
        '''
        minutes = getattr(settings.auth, f'{token_type}_expire')
        expires_delta = datetime.utcnow() + timedelta(minutes=minutes)
        to_encode = {'exp': expires_delta, 'user_email': user_email}
        encoded_jwt = jwt.encode(to_encode, settings.auth.key, settings.auth.algorithms)

        return Token(token=encoded_jwt, expire=int(expires_delta.timestamp()))
