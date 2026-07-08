from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get(self, user_id: int):
        return await self.repo.get(user_id)