from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import selectinload

from app.config.database import async_get_db
from app.constants.constant import ROOT_DIR
from app.models.models import Post
from app.models.schemas import PostResponse
from app.services.post_service import PostService
from app.services.user_service import UserService

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.exceptions import NotFoundException

templates = Jinja2Templates(directory=ROOT_DIR / "templates")


DBSession = Annotated[AsyncSession, Depends(async_get_db)]
post_router = APIRouter()


@post_router.get("/", include_in_schema=False, name="home")
@post_router.get("/blog", include_in_schema=False, name="blog")
async def home_page(request: Request, db: DBSession, page: int = 1, page_size: int = 6):
    post_service = PostService(db)
    paginated = await post_service.paginate(page=page, page_size=page_size)
    return templates.TemplateResponse(
        request,
        "pages/index.html",
        {
            "posts": paginated.items,
            "page": paginated.page,
            "total_pages": paginated.total_pages,
            "total": paginated.total,
        }
    )


@post_router.get("/blog/posts/{post_id}", include_in_schema=False, name="post")
async def post_page(post_id: int, request: Request, db: DBSession):
    post_service = PostService(db)
    post = await post_service.get(post_id, options=[selectinload(Post.author), selectinload(Post.tags), selectinload(Post.category)])
    if post:
        return templates.TemplateResponse(request, "pages/post.html", {"post": post})

    raise NotFoundException(message="Post Not found")


@post_router.get(
    "/users/{user_id}/posts", include_in_schema=False, response_model=list[PostResponse]
)
async def get_user_posts(user_id: int, request: Request, db: DBSession, page: int = 1, page_size: int = 6):
    user_service = UserService(db)
    user = await user_service.get(user_id)
    if not user:
        raise NotFoundException(
            message=f"User with the id: {user_id} doesn't exist!",
        )
    post_service = PostService(db)
    paginated = await post_service.paginate(
        page=page,
        page_size=page_size,
        conditions=[Post.user_id == user_id]
    )

    return templates.TemplateResponse(
        request,
        "pages/user_posts.html",
        {
            "posts": paginated.items,
            "user": user,
            "page": paginated.page,
            "total_pages": paginated.total_pages,
            "total": paginated.total,
        }
    )


@post_router.get("/categories", include_in_schema=False, name="categories")
async def categories(
    request: Request,
    db: DBSession,
    category_id: int | None = None,
    page: int = 1,
    page_size: int = 6
):
    from app.services.category_service import CategoryService
    category_service = CategoryService(db)
    categories_list = await category_service.get_all()
    
    active_category = None
    posts = []
    page_num = 1
    total_pages = 1
    total = 0
    
    if category_id:
        active_category = await category_service.get(category_id)
        if active_category:
            post_service = PostService(db)
            paginated = await post_service.paginate(
                page=page,
                page_size=page_size,
                conditions=[Post.category_id == category_id]
            )
            posts = paginated.items
            page_num = paginated.page
            total_pages = paginated.total_pages
            total = paginated.total
    elif categories_list:
        active_category = categories_list[0]
        post_service = PostService(db)
        paginated = await post_service.paginate(
            page=page,
            page_size=page_size,
            conditions=[Post.category_id == active_category.id]
        )
        posts = paginated.items
        page_num = paginated.page
        total_pages = paginated.total_pages
        total = paginated.total
        
    return templates.TemplateResponse(
        request,
        "pages/categories.html",
        {
            "categories": categories_list,
            "active_category": active_category,
            "posts": posts,
            "page": page_num,
            "total_pages": total_pages,
            "total": total,
        }
    )


@post_router.get("/blog/posts/{post_id}/edit", include_in_schema=False, name="edit_post")
async def edit_post_page(post_id: int, request: Request, db: DBSession):
    post_service = PostService(db)
    post = await post_service.get(post_id, options=[selectinload(Post.tags), selectinload(Post.author), selectinload(Post.category)])
    if not post:
        raise NotFoundException(message="Post Not found")
    
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


@post_router.get("/users/{user_id}/posts/new", include_in_schema=False, name="new_post")
async def new_post_page(user_id: int, request: Request, db: DBSession):
    user_service = UserService(db)
    user = await user_service.get(user_id)
    if not user:
        raise NotFoundException(message=f"User with the id: {user_id} doesn't exist!")
    
    post_service = PostService(db)
    posts = await post_service.get_all_by_user_id(user_id, options=[selectinload(Post.tags)])
    
    from app.services.category_service import CategoryService
    category_service = CategoryService(db)
    categories = await category_service.get_all()
    
    return templates.TemplateResponse(
        request,
        "pages/post_editor.html",
        {
            "post": None,
            "posts": posts,
            "user": user,
            "categories": categories,
        }
    )
