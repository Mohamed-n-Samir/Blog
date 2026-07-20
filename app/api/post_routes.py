from typing import Annotated

from fastapi import APIRouter, Depends, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload 

from app.models.models import Post, User, Comment
from app.models.schemas import PostResponse, PostCreate, CommentCreate, CommentResponse, LikeToggleResponse

from app.services.user_service import UserService
from app.services.post_service import PostService
from app.services.tag_service import TagService

from app.models.models import Tag

from app.utils.exceptions import NotFoundException, AuthorizationException
from app.utils.auth import get_current_user

from app.config.database import async_get_db


DBSession = Annotated[AsyncSession, Depends(async_get_db)]
post_router = APIRouter()


@post_router.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
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
    response_model=PostResponse,
)
async def create_post(
    post: PostCreate,
    db: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if post.user_id != current_user.id:
        raise AuthorizationException("You can only create posts for yourself.")

    user_service = UserService(db)

    if not await user_service.user_exists(post.user_id):
        raise NotFoundException(f"user with id: {post.user_id} does not exist")

    post_data = post.model_dump()
    tag_names = post_data.pop("tags", [])
    new_post = Post(**post_data)

    # Remove duplicates
    tag_names = list(set(tag_names))

    tag_service = TagService(db)

    existing_tags = await tag_service.get_tags_by_names(tag_names)
    existing_by_name = {tag.name: tag for tag in existing_tags}

    new_tags = [
        Tag(name=name)
        for name in tag_names
        if name not in existing_by_name
    ]

    if new_tags:
        await tag_service.add_all(new_tags)

    post_service = PostService(db)

    new_post.tags.extend(existing_tags)
    new_post.tags.extend(new_tags)

    saved_post = await post_service.add(new_post)
        
    return saved_post


@post_router.put(
    "/api/posts/{post_id}",
    response_model=PostResponse,
)
async def update_post(
    post_id: int,
    post: PostCreate,
    db: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    post_service = PostService(db)
    existing_post = await post_service.get(post_id, options=[selectinload(Post.author), selectinload(Post.tags)])
    
    if not existing_post:
        raise NotFoundException(f"Post with id: {post_id} does not exist")

    if existing_post.user_id != current_user.id:
        raise AuthorizationException("You are not authorized to update this post.")

    post_data = post.model_dump()
    tag_names = post_data.pop("tags", [])

    # Update attributes
    existing_post.title = post_data.get("title", existing_post.title)
    existing_post.description = post_data.get("description", existing_post.description)
    existing_post.content = post_data.get("content", existing_post.content)
    existing_post.pinned = post_data.get("pinned", existing_post.pinned)
    existing_post.image_file = post_data.get("image_file", existing_post.image_file)
    existing_post.category_id = post_data.get("category_id", existing_post.category_id)

    # Remove duplicates
    tag_names = list(set(tag_names))

    tag_service = TagService(db)
    existing_tags = await tag_service.get_tags_by_names(tag_names)
    existing_by_name = {tag.name: tag for tag in existing_tags}

    new_tags = [
        Tag(name=name)
        for name in tag_names
        if name not in existing_by_name
    ]

    if new_tags:
        await tag_service.add_all(new_tags)

    existing_post.tags = list(existing_tags) + new_tags

    updated_post = await post_service.update(existing_post)
    return updated_post


@post_router.delete(
    "/api/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: int,
    db: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    post_service = PostService(db)
    existing_post = await post_service.get(post_id)
    if not existing_post:
        raise NotFoundException(f"Post with id: {post_id} does not exist")
    
    if existing_post.user_id != current_user.id:
        raise AuthorizationException("You are not authorized to delete this post.")

    await post_service.delete(post_id)
    return None


@post_router.post("/api/posts/{post_id}/like", response_model=LikeToggleResponse)
async def toggle_post_like(
    post_id: int,
    db: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    post_service = PostService(db)
    post = await post_service.get(post_id, options=[selectinload(Post.likes)])
    if not post:
        raise NotFoundException(f"Post with id: {post_id} does not exist")

    # Check if user already liked the post
    liked = False
    # Since we preloaded post.likes, we can check by id
    user_ids_liked = [u.id for u in post.likes]
    if current_user.id in user_ids_liked:
        # Remove like
        post.likes = [u for u in post.likes if u.id != current_user.id]
        liked = False
    else:
        # Add like
        # We need to fetch current_user with Session db, or merge
        db_user = await db.get(User, current_user.id)
        post.likes.append(db_user)
        liked = True

    await db.commit()
    return LikeToggleResponse(liked=liked, likes_count=len(post.likes))


@post_router.post(
    "/api/posts/{post_id}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentResponse,
)
async def add_post_comment(
    post_id: int,
    comment_in: CommentCreate,
    db: DBSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    post_service = PostService(db)
    post = await post_service.get(post_id)
    if not post:
        raise NotFoundException(f"Post with id: {post_id} does not exist")

    new_comment = Comment(
        content=comment_in.content,
        post_id=post_id,
        user_id=current_user.id
    )
    db.add(new_comment)
    await db.commit()
    
    # Refresh to load relationships (like author)
    stmt = (
        select(Comment)
        .where(Comment.id == new_comment.id)
        .options(selectinload(Comment.author))
    )
    res = await db.scalars(stmt)
    comment_loaded = res.unique().one()
    return comment_loaded


@post_router.get("/api/posts/{post_id}/comments", response_model=list[CommentResponse])
async def get_post_comments(post_id: int, db: DBSession):
    post_service = PostService(db)
    post = await post_service.get(post_id)
    if not post:
        raise NotFoundException(f"Post with id: {post_id} does not exist")

    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    )
    res = await db.scalars(stmt)
    comments = res.unique().all()
    return comments


