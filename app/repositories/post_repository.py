from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Post
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class PostRepository(SQLAlchemyRepository[Post]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Post)
