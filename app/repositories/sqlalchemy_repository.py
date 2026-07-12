from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import func, select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.interfaces import ExecutableOption
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

T = TypeVar("T")


@dataclass(slots=True)
class PaginatedResult(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class SQLAlchemyRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: type[T]):
        self.db = db
        self.model = model
        self._pk = inspect(model).primary_key[0]

    def _build_query(
        self,
        *,
        filters: dict[str, Any] | None = None,
        conditions: Sequence[ColumnElement[bool]] = (),
        options: Sequence[ExecutableOption] = (),
        order_by: (
            Sequence[InstrumentedAttribute[Any] | ColumnElement[Any]] | None
        ) = None,
        distinct: bool = False,
    ) -> Select[tuple[T]]:
        stmt = select(self.model)

        if filters:
            stmt = stmt.filter_by(**filters)

        if conditions:
            stmt = stmt.where(*conditions)

        if options:
            stmt = stmt.options(*options)

        if order_by:
            stmt = stmt.order_by(*order_by)

        if distinct:
            stmt = stmt.distinct()

        return stmt

    async def get(
        self,
        id: Any,
        *,
        options: Sequence[ExecutableOption] = (),
    ) -> T | None:
        return await self.db.get(self.model, id, options=options)

    async def get_all(
        self,
        *,
        options: Sequence[ExecutableOption] = (),
        order_by: (
            Sequence[InstrumentedAttribute[Any] | ColumnElement[Any]] | None
        ) = None,
        distinct: bool = False,
    ) -> Sequence[T]:
        stmt = self._build_query(
            options=options,
            order_by=order_by,
            distinct=distinct,
        )

        result = await self.db.scalars(stmt)
        return result.unique().all()

    async def get_by(
        self,
        *,
        options: Sequence[ExecutableOption] = (),
        **filters: Any,
    ) -> T | None:
        stmt = self._build_query(
            filters=filters,
            options=options,
        )

        result = await self.db.scalars(stmt)
        return result.unique().one_or_none()

    async def get_all_by(
        self,
        *,
        options: Sequence[ExecutableOption] = (),
        order_by: (
            Sequence[InstrumentedAttribute[Any] | ColumnElement[Any]] | None
        ) = None,
        distinct: bool = False,
        **filters: Any,
    ) -> Sequence[T]:
        stmt = self._build_query(
            filters=filters,
            options=options,
            order_by=order_by,
            distinct=distinct,
        )

        result = await self.db.scalars(stmt)
        return result.unique().all()

    async def find(
        self,
        *conditions: ColumnElement[bool],
        options: Sequence[ExecutableOption] = (),
    ) -> T | None:
        stmt = self._build_query(
            conditions=conditions,
            options=options,
        )

        result = await self.db.scalars(stmt)
        return result.unique().one_or_none()

    async def find_all(
        self,
        *conditions: ColumnElement[bool],
        options: Sequence[ExecutableOption] = (),
        order_by: (
            Sequence[InstrumentedAttribute[Any] | ColumnElement[Any]] | None
        ) = None,
        distinct: bool = False,
    ) -> Sequence[T]:
        stmt = self._build_query(
            conditions=conditions,
            options=options,
            order_by=order_by,
            distinct=distinct,
        )

        result = await self.db.scalars(stmt)
        return result.unique().all()

    async def paginate(
        self,
        *conditions: ColumnElement[bool],
        page: int = 1,
        page_size: int = 10,
        options: Sequence[ExecutableOption] = (),
        order_by: (
            Sequence[InstrumentedAttribute[Any] | ColumnElement[Any]] | None
        ) = None,
        distinct: bool = False,
    ) -> PaginatedResult[T]:
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")

        if page_size < 1:
            raise ValueError("page_size must be greater than or equal to 1")

        count_stmt = select(func.count(self._pk))

        if conditions:
            count_stmt = count_stmt.where(*conditions)

        total = await self.db.scalar(count_stmt) or 0

        stmt = (
            self._build_query(
                conditions=conditions,
                options=options,
                order_by=order_by,
                distinct=distinct,
            )
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        result = await self.db.scalars(stmt)
        items = result.unique().all()

        total_pages = (total + page_size - 1) // page_size

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def exists(self, **filters: Any) -> bool:
        stmt = select(select(self.model).filter_by(**filters).exists())
        return bool(await self.db.scalar(stmt))

    # async def add(self, entity: T) -> T:
    #     self.db.add(entity)
    #     await self.db.flush()
    #     await self.db.refresh(entity)
    #     return entity

    async def add(
        self,
        entity: T,
        *,
        attribute_names: Sequence[str] | None = None,
    ) -> T:
        self.db.add(entity)
        await self.db.flush()

        await self.db.refresh(
            entity,
            attribute_names=attribute_names,
        )

        return entity

    async def add_all(self, entities: Sequence[T]) -> Sequence[T]:
        self.db.add_all(entities)
        await self.db.flush()

        for entity in entities:
            await self.db.refresh(entity)

        return entities

    # async def update(self, entity: T) -> T:
    #     merged_entity = await self.db.merge(entity)
    #     await self.db.flush()
    #     return merged_entity
    
    async def update(
        self,
        entity: T,
        *,
        attribute_names: Sequence[str] | None = None,
    ) -> T:
        entity = await self.db.merge(entity)
        await self.db.flush()

        await self.db.refresh(
            entity,
            attribute_names=attribute_names,
        )

        return entity

    async def delete(self, id: Any) -> bool:
        stmt = sqlalchemy_delete(self.model).where(self._pk == id)

        result = await self.db.execute(stmt)
        await self.db.flush()

        return result.rowcount > 0
