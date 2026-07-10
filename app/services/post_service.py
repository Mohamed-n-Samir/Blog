from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.post_repository import PostRepository

from app.models.models import Post

import logging

from app.utils.exceptions import ConflictException

logger = logging.getLogger(__name__)

class PostService:
    def __init__(self, db: AsyncSession):
        self.repo = PostRepository(db)

    async def get(self, post_id: int):
        return await self.repo.get(id=post_id)

    async def get_all(self,options = [selectinload(Post.author)]):
        return await self.repo.get_all(options=options)
    
    async def get_all_by_user_id(self, user_id: int, options=[selectinload(Post.author)]):
        return await self.repo.get_all_by(user_id=user_id, options=options)
    
    async def add(self, post: Post):
        try:
            post = await self.repo.add(post)
            await self.repo.db.commit()
            return post
        except IntegrityError as e:
            await self.repo.db.rollback()
            logger.error("Error while trying to save the newpost", e)
            raise ConflictException(f"Post already exists, {e._message}")
