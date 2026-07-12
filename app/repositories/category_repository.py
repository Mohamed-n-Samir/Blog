from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Category
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class CategoryRepository(SQLAlchemyRepository[Category]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Category)
