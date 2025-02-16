import uuid
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    full_name: Optional[str]
    avatar: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    full_name: str
    avatar: Optional[str]


class UserUpdate(schemas.BaseUserUpdate):
    full_name: str
    avatar: Optional[str]
