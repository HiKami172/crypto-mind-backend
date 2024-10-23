from typing import Any

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str
    keep_logged_in: bool

    class Config:
        from_attributes = True


class RefreshData(BaseModel):
    keep_logged_in: bool = False

    class Config:
        from_attributes = True


class Token(BaseModel):
    token: str
    expire: int = Field(description='Token expire.')


class TokenSchema(BaseModel):
    access_token: Token
    refresh_token: Token | None = Field(default=None, description='Refresh token.')


class TokenData(BaseModel):
    user_email: str | None = Field(default=None, description='User email.')
    expire: int = Field(validation_alias='exp', description='Access token expire.')


class AuthServiceSchema(BaseModel):
    algorithms: str = Field(description='Auth service algorithm.')
    key: str | Any = Field(description='Significant key.')
