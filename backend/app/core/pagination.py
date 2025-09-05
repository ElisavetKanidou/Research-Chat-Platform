
"""
Pagination utilities (app/core/pagination.py)
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

T = TypeVar("T")


class PageParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


class PageResponse(BaseModel, Generic[T]):
    """Paginated response"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
            cls,
            items: List[T],
            total: int,
            page_params: PageParams
    ) -> "PageResponse[T]":
        """Create paginated response"""
        pages = (total + page_params.size - 1) // page_params.size

        return cls(
            items=items,
            total=total,
            page=page_params.page,
            size=page_params.size,
            pages=pages,
            has_next=page_params.page < pages,
            has_prev=page_params.page > 1
        )


async def paginate(
        db: AsyncSession,
        query: Select,
        page_params: PageParams
) -> PageResponse:
    """Paginate a SQLAlchemy query"""

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated items
    paginated_query = query.offset(page_params.offset).limit(page_params.limit)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return PageResponse.create(items, total, page_params)


class CursorParams(BaseModel):
    """Cursor-based pagination parameters"""
    cursor: Optional[str] = None
    limit: int = 20
    order_by: str = "created_at"
    order_direction: str = "desc"


class CursorResponse(BaseModel, Generic[T]):
    """Cursor-based pagination response"""
    items: List[T]
    next_cursor: Optional[str] = None
    has_more: bool = False

    @classmethod
    def create(
            cls,
            items: List[T],
            cursor_field_getter,
            limit: int
    ) -> "CursorResponse[T]":
        """Create cursor-based response"""
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]  # Remove the extra item used for has_more check

        next_cursor = None
        if has_more and items:
            next_cursor = str(cursor_field_getter(items[-1]))

        return cls(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more
        )


def apply_sorting(query: Select, sort_by: str, sort_order: str = "asc") -> Select:
    """Apply sorting to query"""
    if sort_order.lower() == "desc":
        return query.order_by(getattr(query.column_descriptions[0]["type"], sort_by).desc())
    else:
        return query.order_by(getattr(query.column_descriptions[0]["type"], sort_by))


def apply_filters(query: Select, filters: dict) -> Select:
    """Apply filters to query"""
    for field, value in filters.items():
        if value is not None:
            if isinstance(value, str) and "%" in value:
                query = query.where(getattr(query.column_descriptions[0]["type"], field).like(value))
            else:
                query = query.where(getattr(query.column_descriptions[0]["type"], field) == value)

    return query