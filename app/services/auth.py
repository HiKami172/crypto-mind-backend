from datetime import datetime, timedelta
from typing import Callable

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
from app.schemas.users import UserSignIn, UserSignUp
from app.utils.conversions import alchemy_to_dict
from app.utils.password import verify_password, get_hash
from app.utils.unitofwork import IUnitOfWork

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
    fields_to_convert: list[set[str, Callable]] = [
        ('password', get_hash),
    ]

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

    async def signup(self, unit_of_work: IUnitOfWork, user_up: UserSignUp):
        user_data = user_up.model_dump()
        user_dict = self.convert_data_attr(user_data)

        async with unit_of_work:
            user = await unit_of_work.users.create(**user_dict)

        user_response = alchemy_to_dict(user)

        user_response.pop("password", None)

        token = TokenSchema(access_token=self.create_token(user_email=user.email, token_type='access'))
        token.refresh_token = self.create_token(user_email=user.email, token_type='refresh')

        return {
            'response': user_response,
            'token': token
        }

    async def signin(self, user_in: UserSignIn):
        """
        Sign in user.
        Set token to redis and return that.
        :param user_in: UserSignIn
        :return: TokenSchema
        :raises:
                Raise error if existing user has no password (happens if user created from email through token)
                Raise error if password invalid
        """
        user = await self.get_user(user_email=user_in.email)
        user_response = alchemy_to_dict(user)

        user_response.pop("password", None)

        if verify_password(user_in.password, user.password):
            token = TokenSchema(access_token=self.create_token(user_email=user_in.email, token_type='access'))
            if user_in.keep_logged_in:
                token.refresh_token = self.create_token(user_email=user_in.email, token_type='refresh')

            return {
                'response': user_response,
                'token': token
            }

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
        return user

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
        """
        Refresh token.
        :param refresh_token: str
        :return: Token
        """
        try:
            token_data = self.check_token(token=refresh_token)
            return self.create_token(user_email=token_data.user_email)
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpireException
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenSignatureException

    def check_token(self, token: str) -> TokenData:
        """
        Check token in all services.
        :param token: User's token
        :return: TokenData
        :raises:
                Raise error if token expired
        """
        auth_schema = AuthServiceSchema(**settings.auth.model_dump(exclude=['access_expire', 'refresh_expire']))
        try:
            token_data = jwt.decode(token, **auth_schema.model_dump(exclude_unset=True))
            return TokenData(**token_data)
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpireException
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenSignatureException

    def convert_data_attr(self, data: dict) -> dict:
        for attr, func in self.fields_to_convert:
            value = data.get(attr, None)

            if value is not None:
                data[attr] = func(value)

        return data

    @staticmethod
    def create_token(user_email: str, token_type: str = 'access') -> Token:
        """
        Obtain new token.
        :param user_email: User's email
        :param token_type: Token type
        :return: TokenSchema
        """
        minutes = getattr(settings.auth, f'{token_type}_expire')
        expires_delta = datetime.utcnow() + timedelta(minutes=minutes)
        to_encode = {'exp': expires_delta, 'user_email': user_email}
        encoded_jwt = jwt.encode(to_encode, settings.auth.key, settings.auth.algorithms)

        return Token(token=encoded_jwt, expire=int(expires_delta.timestamp()))