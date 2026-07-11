from typing import Annotated

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload 

from app.models.models import Post, User
from app.models.schemas import PostPostResponse, PostCreate

from app.services.user_service import UserService
from app.services.post_service import PostService
from app.services.tag_service import TagService

from app.models.models import Tag

from app.utils.exceptions import NotFoundException

from app.config.database import async_get_db


DBSession = Annotated[AsyncSession, Depends(async_get_db)]
post_router = APIRouter()


@post_router.get("/api/users/{user_id}/posts", response_model=list[PostPostResponse])
async def get_user_posts(user_id: int, db: DBSession):

    user_service = UserService(db)

    if not await user_service.user_exists(id=user_id):
        raise NotFoundException(f"user with id: {id} does not exist")
    
    post_service = PostService(db)

    posts = await post_service.get_all()

    return posts

@post_router.post(
    "/api/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=PostPostResponse,
)
async def create_post(post: PostCreate, tags: list[str], db: DBSession):

    user_service = UserService(db)

    if not await user_service.user_exists(post.user_id):
        raise NotFoundException(f"user with id: {post.user_id} does not exist")

    new_post = Post(**(post.model_dump()))


    # Remove duplicates
    tag_names = list(set(tags))

    tag_service = TagService(db)

    existing_tags = await tag_service.get_tags_by_names(tags)
    existing_by_name = {tag.name: tag for tag in existing_tags}

    new_tags = [
        Tag(name=name)
        for name in tag_names
        if name not in existing_by_name
    ]

    tag_service.add_all(new_tags)

    post_service = PostService(db)

    new_post.tags.extend(existing_tags)
    new_post.tags.extend(new_tags)


    saved_post = await post_service.add(new_post)
        
    return saved_post


