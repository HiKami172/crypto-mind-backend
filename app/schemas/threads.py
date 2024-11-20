from datetime import datetime

from pydantic import UUID4, BaseModel, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class ThreadCreateRequest(BaseModel):
    title: str
    first_message: str = Field(description="First message of the thread.")



class ThreadCreateResponse(BaseModel):
    thread_id: UUID4 = Field(description='Thread ID')


class CreateQuestion(BaseModel):
    text: str = Field(
        description='User question. Must be at least 1 and no more than 500 characters.',
        min_length=1,
    )


class Question(CreateQuestion):
    pk: str = Field(alias="thread_id", description='Thread ID')


class MessageMain(BaseModel):
    id: UUID4
    text: str = Field(description='Message text')
    type: str = Field(description='Message type', examples=['user', 'assistant', 'tool'])
    created_at: datetime = Field(description='Message creation datetime')
    thread_id: UUID4 = Field(description='Thread ID message belongs to')

    @field_validator('id', 'thread_id')
    @classmethod
    def uuid_to_str(cls, value: UUID4, _: FieldValidationInfo) -> str | None:
        return str(value) if value else None

    @field_validator('created_at')
    @classmethod
    def datetime_to_str(cls, value: datetime, _: FieldValidationInfo) -> str:
        return value.isoformat()

    class Config:
        from_attributes = True


class FilterQuery(BaseModel):
    text: str | None = Field(description='Filter by text', default=None)


class Thread(BaseModel):
    id: UUID4 = Field(description='Thread ID')
    title: str = Field(description='Thread title')
    created_at: datetime = Field(description='Thread creation date')
    updated_at: datetime = Field(description='Thread updated date')

    @field_validator('id')
    @classmethod
    def uuid_to_str(cls, value: UUID4, _: FieldValidationInfo) -> str:
        return str(value)

    @field_validator('created_at', 'updated_at')
    @classmethod
    def datetime_to_str(cls, value: datetime, _: FieldValidationInfo) -> str:
        return value.isoformat()

    class Config:
        from_attributes = True


class ThreadList(BaseModel):
    threads: list[Thread] = Field(description='List of threads')

    def model_dump(self, *args, **kwargs) -> list[dict]:
        return [thread.model_dump() for thread in self.threads]

    class Config:
        from_attributes = True


class ThreadRetrieveRequest(BaseModel):
    id: UUID4 = Field(description='Thread ID')


class ThreadMessagesByIdResponse(Thread):
    messages: list[MessageMain]

    class Config:
        from_attributes = True
