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

    async def get(
        self, post_id: int, options=[selectinload(Post.author), selectinload(Post.tags)]
    ):
        return await self.repo.get(id=post_id, options=options)

    async def get_all(self, options=[selectinload(Post.author)]):
        return await self.repo.get_all(options=options)

    async def get_all_by_user_id(
        self, user_id: int, options=[selectinload(Post.author)]
    ):
        return await self.repo.get_all_by(user_id=user_id, options=options)

    async def paginate(
        self,
        *,
        page: int = 1,
        page_size: int = 6,
        conditions: list = [],
        options = [
            selectinload(Post.author),
            selectinload(Post.tags),
            selectinload(Post.category),
        ]
    ):
        return await self.repo.paginate(
            *conditions,
            page=page,
            page_size=page_size,
            options=options,
            order_by=[Post.pinned.desc(), Post.created_at.desc()]
        )

    async def add(self, post: Post):
        try:
            new_post = await self.repo.add(
                post,
                attribute_names=["author", "category"],
            )
            await self.repo.db.commit()
            return new_post
        except IntegrityError as e:
            await self.repo.db.rollback()
            logger.error("Error while trying to save the newpost", e)
            raise ConflictException(f"Post already exists, {e._message}")

    async def update(self, post: Post):
        try:
            post = await self.repo.update(post)
            await self.repo.db.commit()
            return post
        except IntegrityError as e:
            await self.repo.db.rollback()
            logger.error("Error while trying to update the post", e)
            raise ConflictException(f"Error updating post, {e._message}")

    async def delete(self, post_id: int) -> bool:
        try:
            deleted = await self.repo.delete(post_id)
            await self.repo.db.commit()
            return deleted
        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error while trying to delete the post {post_id}", e)
            raise ConflictException(f"Error deleting post, {str(e)}")
