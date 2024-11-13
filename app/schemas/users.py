from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.schemas import mixins
from app.schemas.mixins import EmailRequiredMixin

PhoneNumber.phone_format = 'E164'

class UserBase(EmailRequiredMixin, BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)



class UserUpdate(mixins.PasswordRequiredMixin, BaseModel):
    name: str
    phone: PhoneNumber


class UserPartialUpdate(mixins.PhoneMixin, mixins.PasswordRequiredMixin, BaseModel):
    check_password: str | None = Field(
        alias='password2',
        default=None,
        min_length=8,
        max_length=50,
        description='Check password. Must be at least 8 and no more than 50 characters.',
        exclude=True,
    )

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=50,
        description='User password. Must be at least 8 and no more than 50 characters.',
    )


class UserSignIn(mixins.EmailRequiredMixin, BaseModel):
    model_config = ConfigDict(from_attributes=True)

    password: str = Field(
        min_length=8,
        max_length=50,
        description='User password. Must be at least 8 and no more than 50 characters.',
    )
    keep_logged_in: bool = Field(
        default=False,
        description='Generate a refresh token for the user.',
    )


class UserSignUp(
    mixins.EmailRequiredMixin,
    mixins.PasswordRequiredMixin,
    BaseModel,
):
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserList(mixins.EmailRequiredMixin, BaseModel):
    id: int
    name: str
    email: str

