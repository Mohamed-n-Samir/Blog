from typing import Annotated

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import async_get_db
from app.constants.constant import ROOT_DIR
from app.models.models import Post
from app.services.post_service import PostService
from app.config.templates import templates

DBSession = Annotated[AsyncSession, Depends(async_get_db)]
main_router = APIRouter()


@main_router.get("/", include_in_schema=False, name="home")
@main_router.get("/blog", include_in_schema=False, name="blog")
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


@main_router.get("/categories", include_in_schema=False, name="categories")
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
