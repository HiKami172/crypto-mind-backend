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
    ):
        self.session = session
        self.fetch_method = fetch_method
        self.query = query
        self.page = page
        self.per_page = self.limit = per_page
        self.offset = (page - 1) * per_page
        self.request = request_object.get()
        self.extra_page = add_extra_page
        # computed later
        self.number_of_pages = 0
        self.next_page = ''
        self.previous_page = ''

    def _get_next_page(self) -> str | None:
        if self.page >= self.number_of_pages:
            return
        url = self.request.url.include_query_params(page=self.page + 1)
        return str(url)

    def _get_previous_page(self) -> str | None:
        if self.page == 1:
            return
        if self.page > self.number_of_pages:
            if not self.extra_page:
                return
            # Last page
            url = self.request.url.include_query_params(page=self.number_of_pages - 1)
            self.offset = (self.number_of_pages - 1) * self.per_page
        else:
            # Previous page
            url = self.request.url.include_query_params(page=self.page - 1)
        return str(url)

    async def get_response(self) -> dict:
        return {
            'count': await self._get_total_count(),
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
) -> dict:
    paginator = Paginator(
        session,
        query,
        page,
        per_page,
        fetch_method=fetch_method,
        add_extra_page=add_extra_page,
    )
    return await paginator.get_response()
