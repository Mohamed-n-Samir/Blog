from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class SQLAlchemyRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: type[T]):
        self.db = db
        self.model = model

    async def get(self, id: int) -> T | None:
        return await self.db.get(self.model, id)

    async def get_all(self) -> list[T]:
        result = await self.db.scalars(select(self.model))
        return list(result.all())

    async def add(self, entity: T) -> T:
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete(self, id: int) -> bool:
        entity = await self.get(id)

        if entity is None:
            return False

        await self.db.delete(entity)
        await self.db.commit()

        return True