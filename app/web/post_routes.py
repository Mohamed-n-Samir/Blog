from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import async_get_db
from app.constants.constant import ROOT_DIR
from app.models.models import Post
from app.services.post_service import PostService
from app.services.user_service import UserService
from app.utils.exceptions import NotFoundException
from app.config.templates import templates

DBSession = Annotated[AsyncSession, Depends(async_get_db)]
post_router = APIRouter()


@post_router.get("/blog/posts/{post_id}", include_in_schema=False, name="post")
async def post_page(post_id: int, request: Request, db: DBSession):
    post_service = PostService(db)
    post = await post_service.get(post_id, options=[selectinload(Post.author), selectinload(Post.tags), selectinload(Post.category)])
    if post:
        return templates.TemplateResponse(request, "pages/post.html", {"post": post})

    raise NotFoundException(message="Post Not found")


@post_router.get("/blog/posts/{post_id}/edit", include_in_schema=False, name="edit_post")
async def edit_post_page(post_id: int, request: Request, db: DBSession):
    post_service = PostService(db)
    post = await post_service.get(post_id, options=[selectinload(Post.tags), selectinload(Post.author), selectinload(Post.category)])
    if not post:
        raise NotFoundException(message="Post Not found")
    
    current_user = request.state.user
    if not current_user or current_user.id != post.user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this post.")
        
    posts = await post_service.get_all_by_user_id(post.user_id, options=[selectinload(Post.tags)])
    
    from app.services.category_service import CategoryService
    category_service = CategoryService(db)
    categories = await category_service.get_all()
    
    return templates.TemplateResponse(
        request,
        "pages/post_editor.html",
        {
            "post": post,
            "posts": posts,
            "user": post.author,
            "categories": categories,
        }
    )


@post_router.get("/posts/new", include_in_schema=False, name="new_post")
async def new_post_page(request: Request, db: DBSession):
    current_user = request.state.user
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    post_service = PostService(db)
    posts = await post_service.get_all_by_user_id(current_user.id, options=[selectinload(Post.tags)])
    
    from app.services.category_service import CategoryService
    category_service = CategoryService(db)
    categories = await category_service.get_all()
    
    return templates.TemplateResponse(
        request,
        "pages/post_editor.html",
        {
            "post": None,
            "posts": posts,
            "user": current_user,
            "categories": categories,
        }
    )
