from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.category_repository import CategoryRepository
from app.models.models import Category


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepository(db)

    async def get(self, category_id: int):
        return await self.repo.get(id=category_id)

    async def get_all(self):
        return await self.repo.get_all()

    async def get_by_name(self, name: str):
        return await self.repo.get_by(name=name)

    async def add(self, category: Category):
        category = await self.repo.add(category)
        await self.repo.db.commit()
        return category
