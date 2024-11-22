import uuid
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    full_name: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    full_name: str


class UserUpdate(schemas.BaseUserUpdate):
    full_name: str
