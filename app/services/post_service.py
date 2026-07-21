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
        self, post_id: int, options=[selectinload(Post.author), selectinload(Post.tags), selectinload(Post.likes), selectinload(Post.comments)]
    ):
        return await self.repo.get(id=post_id, options=options)

    async def get_all(self, options=[selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments)]):
        return await self.repo.get_all(options=options)

    async def get_all_by_user_id(
        self, user_id: int, options=[selectinload(Post.author), selectinload(Post.likes), selectinload(Post.comments)]
    ):
        return await self.repo.get_all_by(user_id=user_id, options=options)

    async def paginate(
        self,
        *,
        page: int = 1,
        page_size: int = 6,
        conditions: list = [],
        sort_by: str | None = None,
        tag: str | None = None,
        options=[
            selectinload(Post.author),
            selectinload(Post.tags),
            selectinload(Post.category),
            selectinload(Post.likes),
            selectinload(Post.comments),
        ],
    ):
        from sqlalchemy import func, select
        from app.models.models import post_likes, Comment, Tag

        local_conditions = list(conditions)

        if tag:
            local_conditions.append(Post.tags.any(Tag.name == tag))

        order_by = [Post.pinned.desc()]
        if sort_by == "likes":
            likes_subquery = (
                select(func.count(post_likes.c.user_id))
                .where(post_likes.c.post_id == Post.id)
                .scalar_subquery()
            )
            order_by.append(likes_subquery.desc())
        elif sort_by == "comments":
            comments_subquery = (
                select(func.count(Comment.id))
                .where(Comment.post_id == Post.id)
                .scalar_subquery()
            )
            order_by.append(comments_subquery.desc())

        order_by.append(Post.created_at.desc())

        return await self.repo.paginate(
            *local_conditions,
            page=page,
            page_size=page_size,
            options=options,
            order_by=order_by,
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
            post = await self.repo.update(post, attribute_names=["author", "category"])
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
