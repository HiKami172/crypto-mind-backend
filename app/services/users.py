from typing import Callable

from app.exceptions.auth_exceptions import PermissionDenied
from app.models import User
from app.schemas.users import UserPartialUpdate, UserSignUp, UserUpdate
from app.utils.conversions import alchemy_to_dict
from app.utils.password import get_hash
from app.utils.unitofwork import IUnitOfWork


class UserService:
    fields_to_convert: list[set[str, Callable]] = [('password', get_hash)]

    async def create(self, unit_of_work: IUnitOfWork, user: UserSignUp) -> User:
        data = user.model_dump()
        user_dict = self.convert_data_attr(data)
        async with unit_of_work:
            user = await unit_of_work.users.create(**user_dict)

        return user

    async def list(self, unit_of_work: IUnitOfWork, page: int, per_page: int, **filter_by) -> dict:
        async with unit_of_work:
            return await unit_of_work.users.list(page=page, per_page=per_page, **filter_by)

    async def retrieve(self, unit_of_work: IUnitOfWork, user_id: int) -> User:
        async with unit_of_work:
            user = await unit_of_work.users.retrieve(pk=user_id)
        user_response = alchemy_to_dict(user)
        user_response.pop("password", None)
        return user_response

    async def update(
        self,
        unit_of_work: IUnitOfWork,
        user_id: int,
        data: UserUpdate | UserPartialUpdate,
        current_user_id: int,
        partial: bool = False,
    ) -> User:
        if user_id != current_user_id:
            raise PermissionDenied('You can\'t edit anybody else account.')

        user_dict = self.convert_data_attr(data.model_dump(exclude_unset=partial))

        async with unit_of_work:
            user = await unit_of_work.users.update(pk=user_id, data=user_dict)

        return user

    async def partial_update(
        self, unit_of_work: IUnitOfWork, user_id: int, data: UserPartialUpdate, current_user_id: int
    ) -> User:
        return await self.update(
            user_id=user_id,
            data=data,
            partial=True,
            unit_of_work=unit_of_work,
            current_user_id=current_user_id,
        )

    async def destroy(self, unit_of_work: IUnitOfWork, user_id: int, current_user_id: int) -> None:
        async with unit_of_work:

            if user_id != current_user_id:
                raise PermissionDenied('You can\'t delete anybody else account.')

            await unit_of_work.users.delete(pk=user_id)
            await unit_of_work.commit()
            await self.drop_jwt(user_id)

    async def delete(self, unit_of_work: IUnitOfWork, user_id: int, current_user_id: int) -> None:
        async with unit_of_work:

            if user_id != current_user_id:
                raise PermissionDenied('You can\'t delete anybody else account.')

            await unit_of_work.users.update(pk=user_id, data={'is_active': False})
            await unit_of_work.commit()
            await self.drop_jwt(user_id)

    async def drop_jwt(self, user_id):
        raise NotImplemented

    def convert_data_attr(self, data: dict) -> dict:
        for attr, func in self.fields_to_convert:
            value = data.get(attr, None)

            if value is not None:
                data[attr] = func(value)

        return data
