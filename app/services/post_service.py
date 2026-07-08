from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.post_repository import PostRepository

class PostService:
    def __init__(self, db: AsyncSession):
        self.repo = PostRepository(db)

    async def get(self, post_id: int):
        return await self.repo.get(post_id)

    async def get_all(self):
        return await self.repo.get_all()
    
    async def get_all_by_user_id(self, user_id: int):
        return await self.repo.get_all_by_user_id(user_id)