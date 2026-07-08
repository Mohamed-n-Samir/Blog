from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Post
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class PostRepository(SQLAlchemyRepository[Post]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Post)

    async def get_all_by_user_id(self, user_id: int) -> list[Post]:
        result = await self.db.scalars(select(self.model).where(self.model.user_id == user_id))
        return list(result.all())
