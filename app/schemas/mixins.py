from pydantic import BaseModel, EmailStr, Field, FieldValidationInfo, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

PhoneNumber.phone_format = 'E164'


class PasswordRequiredMixin(BaseModel):
    check_password: str = Field(
        alias='password2',
        min_length=8,
        max_length=50,
        description='Check password. Must be at least 8 and no more than 50 characters.',
        exclude=True,
    )
    password: str = Field(
        alias='password',
        min_length=8,
        max_length=50,
        description='User password. Must be at least 8 and no more than 50 characters.',
    )

    @field_validator('password')
    @classmethod
    def passwords_match(cls, v: str, info: FieldValidationInfo) -> str:
        if 'check_password' in info.data and v != info.data['check_password']:
            raise ValueError('passwords do not match')
        info.data['check_password'] = None
        return v


class EmailRequiredMixin(BaseModel):
    email: EmailStr = Field(description='User e-mail.', examples=['test@example.com'])


class PhoneMixin(BaseModel):
    phone: PhoneNumber = Field(description='Phone number in E164 format.', examples=['+380991234567'])
