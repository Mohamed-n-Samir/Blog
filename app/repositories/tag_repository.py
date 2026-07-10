from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Tag
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class TagRepository(SQLAlchemyRepository[Tag]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Tag)