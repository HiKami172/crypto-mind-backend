from typing import Callable

from sqlalchemy import Result, Row, SelectBase, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.middlewares.context import request_object


class Paginator:
    def __init__(
        self,
        session: AsyncSession,
        query: SelectBase,
        page: int,
        per_page: int,
        fetch_method: str = 'scalars',
        add_extra_page: bool = False,
        is_reversed: bool = False  # New attribute for reversed pagination
    ):
        self.session = session
        self.fetch_method = fetch_method
        self.query = query
        self.page = page
        self.per_page = self.limit = per_page
        self.offset = 0
        self.is_reversed = is_reversed
        self.request = request_object.get()
        self.extra_page = add_extra_page
        self.number_of_pages = 0
        self.next_page = None
        self.previous_page = None

    def _get_next_page(self) -> int | None:
        if self.page >= self.number_of_pages:
            return None
        return self.page + 1

    def _get_previous_page(self) -> int | None:
        if self.page <= 1:
            return None
        if self.page > self.number_of_pages:
            if not self.extra_page:
                return None
            self.offset = (self.number_of_pages - 1) * self.per_page
            return self.number_of_pages - 1
        return self.page - 1

    async def get_response(self) -> dict:
        count = await self._get_total_count()
        if self.is_reversed:
            offset = count - (self.page * self.per_page)
            if offset < 0:
                self.limit = offset + self.per_page
                offset = 0
            self.offset = offset
        else:
            self.offset = (self.page - 1) * self.per_page
        return {
            'offset': self.offset,
            'count': count,
            'next_page': self._get_next_page(),
            'previous_page': self._get_previous_page(),
            'items': await self._get_items(),
        }

    async def _get_items(self) -> list:
        statement = self.query.limit(self.limit).offset(self.offset)
        results: Result = await self.session.execute(statement)
        method: Callable = getattr(results, self.fetch_method)
        data = method()
        items = []
        if data:
            for item in data:
                if isinstance(item, Row):
                    item = item._mapping
                items.append(item)
        return items

    def _get_number_of_pages(self, count: int) -> int:
        quotient, rest = divmod(count, self.per_page)
        return quotient if not rest else quotient + 1

    async def _get_total_count(self) -> int:
        count = await self.session.scalar(select(func.count()).select_from(self.query.subquery()))
        self.number_of_pages = self._get_number_of_pages(count)
        return count


async def paginate(
    session: AsyncSession,
    query: SelectBase,
    page: int,
    per_page: int,
    fetch_method: str = 'scalars',
    add_extra_page: bool = False,
    is_reversed: bool = False
) -> dict:
    paginator = Paginator(
        session,
        query,
        page,
        per_page,
        fetch_method=fetch_method,
        add_extra_page=add_extra_page,
        is_reversed=is_reversed
    )
    return await paginator.get_response()
