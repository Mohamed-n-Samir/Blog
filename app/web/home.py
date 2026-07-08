from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates

from app.config.database import async_get_db
from app.constants.constant import ROOT_DIR
from app.models import models
from app.models.schemas import PostResponse
from app.services.post_service import PostService
from app.services.user_service import UserService

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


templates = Jinja2Templates(directory=ROOT_DIR / "templates")


DBSession = Annotated[AsyncSession, Depends(async_get_db)]
home_router = APIRouter()


@home_router.get("/", include_in_schema=False, name="home")
@home_router.get("/blog", include_in_schema=False, name="blog")
async def home_page(request: Request, db: DBSession):
    post_service = PostService(db)
    posts = await post_service.get_all()
    return templates.TemplateResponse(request, "pages/index.html", {"posts": posts})


@home_router.get("/blog/posts/{post_id}", include_in_schema=False, name="post")
async def post_page(post_id: int, request: Request, db: DBSession):
    post_service = PostService(db)
    post = await post_service.get(post_id)
    if post:
        return templates.TemplateResponse(request, "pages/post.html", {"post": post})

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not found")


@home_router.get(
    "/users/{user_id}/posts", include_in_schema=False, response_model=list[PostResponse]
)
async def get_user_posts(user_id: int, request: Request,db: DBSession):
    user_service = UserService()
    user = await user_service.get(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the id: {user_id} doesn't exist!",
        )
    post_service = PostService()
    posts = await post_service.get_all_by_user_id(user_id)

    return templates.TemplateResponse(request, "pages/user_posts.html", {"posts": posts, 'user': user})


@home_router.get("/categories", include_in_schema=False, name="categories")
def categories(request: Request):
    return templates.TemplateResponse(request, "pages/categories.html")