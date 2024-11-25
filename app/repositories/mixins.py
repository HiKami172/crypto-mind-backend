from sqlalchemy import select

from app.utils.paginator import paginate


class PaginateListMixins:
    async def list(self, *, page: int | None, per_page: int | None, is_reversed=False, **filter_by) -> dict:
        page = page or 1
        per_page = per_page or 10

        statement = select(self.model).filter_by(**filter_by)  # noqa

        return await paginate(self.session, statement, page=page, per_page=per_page, is_reversed=is_reversed)  # noqa
