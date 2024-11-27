from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

from loguru import logger

from sqlalchemy import Result, ScalarResult, delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.request_exceptions import EntryAlreadyExistsException, NotFoundException

M = TypeVar('M')


class AbstractRepository(ABC):
    @abstractmethod
    async def create(self, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def list(self, **filter_by):
        raise NotImplemented

    @abstractmethod
    async def retrieve(self, return_result: bool = False, **whereclauses):
        raise NotImplemented

    @abstractmethod
    async def update(self, data: dict, **whereclauses):
        raise NotImplemented

    @abstractmethod
    async def delete(self, pk: int | str):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model: Generic[M]
    unique_rows = set()
    default_order_by = 'id'

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model_name = self.model.__name__

    async def create(self, **kwargs) -> M:
        logger.debug('Adding new {model_name}', model_name=self.model_name.lower())

        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def list(
        self, *, limit: int = None, offset: int = None, order_by: list[str] = None, **filter_by
    ) -> ScalarResult[M]:
        order_by = order_by or [self.default_order_by]

        statement = select(self.model).filter_by(**filter_by).order_by(*self.get_order_by_clauses(*order_by))

        if limit:
            statement = statement.limit(limit)

        if offset:
            statement = statement.offset(offset)

        result: Result = await self.execute(statement)

        return await self.fetch_data(result.scalars)

    async def retrieve(self, return_result: bool = False, **whereclauses) -> M | None | Result:
        statement = select(self.model).where(*self.get_where_clauses(**whereclauses))
        result: Result = await self.execute(statement)

        return result if return_result else await self.fetch_data(result.scalar_one)

    async def update(self, data: dict, **whereclauses) -> M:
        logger.debug(
            'Editing {model_name} with id={id}',
            model_name=self.model_name.lower(),
            id=whereclauses.get('pk') or whereclauses.get('id'),
        )
        statement = (
            update(self.model).where(*self.get_where_clauses(**whereclauses)).values(**data).returning(self.model)
        )
        result: Result = await self.execute(statement)

        return await self.fetch_data(result.scalar_one)

    async def delete(self, **whereclauses) -> None:
        logger.debug(
            'Deleting {model_name} with id={id}',
            model_name=self.model_name.lower(),
            id=whereclauses.get('pk') or whereclauses.get('id'),
        )
        statement = delete(self.model).where(*self.get_where_clauses(**whereclauses))
        await self.execute(statement)

    async def execute(self, statement) -> Result:
        try:
            return await self.session.execute(statement)
        except IntegrityError as e:
            logger.exception('IntegrityError: {e}', e=e)
            if 'duplicate' in str(e):
                raise EntryAlreadyExistsException(
                    class_name=self.model_name,
                    unique_rows=' or '.join(self.unique_rows),
                )
            raise e

    async def exists(self, **whereclauses) -> bool:
        statement = select(self.model).where(*self.get_where_clauses(**whereclauses))
        result: Result = await self.execute(statement)
        return bool(result.scalar_one_or_none())

    async def fetch_data(self, action: Callable) -> ScalarResult[M] | M:
        try:
            return action()
        except NoResultFound:
            raise NotFoundException(class_name=self.model_name)

    def get_where_clauses(self, **kwargs) -> list:
        if 'pk' in kwargs:
            kwargs['id'] = kwargs.pop('pk')
        return (getattr(self.model, key) == value for key, value in kwargs.items())

    def get_order_by_clauses(self, *args) -> list:
        ret = []
        for arg in args:
            decs_flag = False
            _attr = None

            if arg.startswith('-'):
                decs_flag = True
                arg = arg[1:]

            for lookup in arg.split('__'):
                if _attr:
                    _attr = getattr(_attr, lookup)
                else:
                    _attr = getattr(self.model, lookup)

            if decs_flag:
                _attr = _attr.desc()

            ret.append(_attr)

        return ret

    async def get_or_create(self, return_result: bool = False, **kwargs) -> M:
        try:
            return await self.retrieve(return_result=return_result, **kwargs)
        except NotFoundException:
            kwargs.pop('pk', None)
            kwargs.pop('id', None)
            return await self.create(**kwargs)

    async def get_object_or_none(self, **kwargs):
        result: Result = await self.retrieve(return_result=True, **kwargs)
        return await self.fetch_data(result.scalar_one_or_none)

    async def get_first_object(self, **kwargs):
        result: Result = await self.retrieve(return_result=True, **kwargs)
        data = await self.fetch_data(result.first)
        if not data:
            return None
        return data[0]
