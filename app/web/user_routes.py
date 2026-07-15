from typing import Annotated

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import async_get_db
from app.constants.constant import ROOT_DIR
from app.models.models import Post
from app.models.schemas import PostResponse
from app.services.post_service import PostService
from app.services.user_service import UserService
from app.utils.exceptions import NotFoundException
from app.utils.image_uploader import save_uploaded_image

templates = Jinja2Templates(directory=ROOT_DIR / "templates")
DBSession = Annotated[AsyncSession, Depends(async_get_db)]
user_router = APIRouter()


@user_router.get(
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


@user_router.get("/users/{user_id}/profile", include_in_schema=False, name="user_profile")
async def user_profile_page(user_id: int, request: Request, db: DBSession):
    user_service = UserService(db)
    user = await user_service.get(user_id)
    if not user:
        raise NotFoundException(message=f"User with the id: {user_id} doesn't exist!")
    
    return templates.TemplateResponse(
        request,
        "pages/user_profile.html",
        {
            "user": user,
            "error": None,
            "success": None,
        }
    )


@user_router.post("/users/{user_id}/profile", include_in_schema=False)
async def update_profile(
    user_id: int,
    request: Request,
    db: DBSession,
    username: str = Form(...),
    email: str = Form(...),
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
    bio: str | None = Form(None),
    image: UploadFile = File(None)
):
    user_service = UserService(db)
    user = await user_service.get(user_id)
    if not user:
        raise NotFoundException(message=f"User with the id: {user_id} doesn't exist!")
    
    username = username.strip()
    email = email.strip()
    first_name = first_name.strip() if first_name else None
    last_name = last_name.strip() if last_name else None
    bio = bio.strip() if bio else None
    
    error_msg = None
    success_msg = None
    
    try:
        # Save image file if uploaded
        if image and image.filename:
            uploaded_filename = await save_uploaded_image(image, "profile_pics")
            user.image_file = uploaded_filename
    
        # Validate uniqueness if username or email changed
        if username != user.username or email != user.email:
            await user_service.validate_unique_user(
                username=username,
                email=email,
                exclude_user_id=user_id
            )
        
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        
        await user_service.update(user)
        success_msg = "Profile updated successfully!"
    except Exception as e:
        error_msg = str(e)
        
    return templates.TemplateResponse(
        request,
        "pages/user_profile.html",
        {
            "user": user,
            "error": error_msg,
            "success": success_msg,
        }
    )
