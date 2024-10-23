from fastapi import APIRouter, Cookie
from fastapi.responses import Response

from app.settings import settings
from app.routers.dependencies import get_auth_service
from app.schemas.auth import Token
from app.schemas.users import UserSignIn

router = APIRouter(tags=['Auth'])


@router.post(
    '/login/',
    description='Obtain access token via user credentials.',
)
async def login(data: UserSignIn, auth_service: get_auth_service):
    result = await auth_service.signin(user_in=data)
    response = Response(result.json(exclude_none=True))
    if data.keep_logged_in:
        response.set_cookie(
            key='refresh_token',
            value=result.refresh_token.token,
            httponly=True,
            max_age=settings.auth.refresh_expire * 60,
            expires=settings.auth.refresh_expire * 60,
            secure=True,
            samesite="none"
        )
    return response


@router.post(
    '/refresh/',
    response_model=Token,
    description='Obtain new access token from refresh token',
)
async def refresh(auth_service: get_auth_service, refresh_token: str = Cookie(None)):
    return await auth_service.refresh_token(refresh_token=refresh_token)


@router.get(
    '/logout/',
    description='Remove refresh token',
)
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"status": "success"}
