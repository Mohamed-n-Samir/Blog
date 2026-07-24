from typing import Annotated

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import async_get_db
from app.constants.constant import ROOT_DIR
from app.models.models import Post, User
from app.models.schemas import PostResponse
from app.services.post_service import PostService
from app.services.user_service import UserService
from app.services.tag_service import TagService
from app.utils.exceptions import APPException, NotFoundException, AuthenticationException
from app.utils.image_operations import save_uploaded_image
from app.config.templates import templates

DBSession = Annotated[AsyncSession, Depends(async_get_db)]
user_router = APIRouter()


@user_router.get(
    "/users/{user_id}/posts", include_in_schema=False, response_model=list[PostResponse]
)
async def get_user_posts(
    user_id: int,
    request: Request,
    db: DBSession,
    page: int = 1,
    page_size: int = 6,
    sort_by: str | None = None,
    tag: str | None = None
):
    current_user = request.state.user
    print(f"[DEBUG] get_user_posts: current_user={current_user}")
    if current_user:
        print(f"[DEBUG] get_user_posts: current_user.id={current_user.id} type={type(current_user.id)}")
        
    res = await db.scalars(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.followers))
    )
    user = res.unique().one_or_none()
    if not user:
        raise NotFoundException(
            message=f"User with the id: {user_id} doesn't exist!",
        )
    post_service = PostService(db)
    tag_service = TagService(db)
    
    paginated = await post_service.paginate(
        page=page,
        page_size=page_size,
        conditions=[Post.user_id == user_id],
        sort_by=sort_by,
        tag=tag
    )
    all_tags = await tag_service.get_all()

    return templates.TemplateResponse(
        request,
        "pages/user_posts.html",
        {
            "posts": paginated.items,
            "user": user,
            "page": paginated.page,
            "total_pages": paginated.total_pages,
            "total": paginated.total,
            "all_tags": all_tags,
            "sort_by": sort_by,
            "tag": tag,
        }
    )


@user_router.get("/profile", include_in_schema=False, name="user_profile")
async def user_profile_page(request: Request, db: DBSession):
    current_user = request.state.user
    if not current_user:
        raise AuthenticationException("Not authenticated")
    
    return templates.TemplateResponse(
        request,
        "pages/user_profile.html",
        {
            "user": current_user,
            "error": None,
            "success": None,
        }
    )


@user_router.post("/profile", include_in_schema=False, name="update_profile")
async def update_profile(
    request: Request,
    db: DBSession,
    username: str = Form(...),
    email: str = Form(...),
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
    bio: str | None = Form(None),
    image: UploadFile = File(None)
):
    current_user = request.state.user
    if not current_user:
        raise AuthenticationException("Not authenticated")
    
    username = username.strip()
    email = email.strip()
    first_name = first_name.strip() if first_name else None
    last_name = last_name.strip() if last_name else None
    bio = bio.strip() if bio else None
    
    error_msg = None
    success_msg = None
    
    try:
        user_service = UserService(db)
        # Save image file if uploaded
        if image and image.filename:
            
            uploaded_filename = await save_uploaded_image(image, "profile_pics")
            current_user.image_file = uploaded_filename
    
        # Validate uniqueness if username or email changed
        if username != current_user.username or email != current_user.email:
            await user_service.validate_unique_user(
                username=username,
                email=email,
                exclude_user_id=current_user.id
            )
        
        current_user.username = username
        current_user.email = email
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.bio = bio
        
        await user_service.update(current_user)
        success_msg = "Profile updated successfully!"
    except Exception as e:
        error_msg = str(e)
        
    return templates.TemplateResponse(
        request,
        "pages/user_profile.html",
        {
            "user": current_user,
            "error": error_msg,
            "success": success_msg,
        }
    )


from sqlalchemy import func, select, or_
from sqlalchemy.orm import selectinload
from app.models.models import User, followers

@user_router.get("/users/search", include_in_schema=False, name="search_users")
async def search_users(
    request: Request,
    db: DBSession,
    q: str | None = None,
    page: int = 1,
    page_size: int = 6
):
    # Subquery to aggregate follower counts
    follower_count_sub = (
        select(followers.c.followed_id, func.count(followers.c.follower_id).label("follower_count"))
        .group_by(followers.c.followed_id)
        .subquery()
    )
    
    current_user = request.state.user
    print(f"[DEBUG] search_users: current_user={current_user}")
    if current_user:
        print(f"[DEBUG] search_users: current_user.id={current_user.id} type={type(current_user.id)}")
        
    conditions = []
    if q:
        q = q.strip()
        conditions.append(
            or_(
                User.username.ilike(f"%{q}%"),
                User.first_name.ilike(f"%{q}%"),
                User.last_name.ilike(f"%{q}%")
            )
        )
        
    if current_user:
        conditions.append(User.id != current_user.id)
        
    # Count total matching users
    count_stmt = select(func.count(User.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = await db.scalar(count_stmt) or 0
    
    # Query matching users sorted by follower count descending
    stmt = (
        select(User)
        .outerjoin(follower_count_sub, User.id == follower_count_sub.c.followed_id)
        .options(selectinload(User.followers))
        .order_by(follower_count_sub.c.follower_count.desc().nullslast(), User.username.asc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    if conditions:
        stmt = stmt.where(*conditions)
        
    result = await db.scalars(stmt)
    users_list = result.unique().all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return templates.TemplateResponse(
        request,
        "pages/users_search.html",
        {
            "users": users_list,
            "query": q,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        }
    )


@user_router.get("/connections", include_in_schema=False, name="user_connections")
async def user_connections_page(request: Request, db: DBSession):
    current_user = request.state.user
    if not current_user:
        raise AuthenticationException("Not authenticated")
    
    # Re-fetch current_user with both following and followers loaded
    res = await db.scalars(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.following).selectinload(User.followers),
            selectinload(User.followers).selectinload(User.followers)
        )
    )
    user = res.unique().one()
    
    following_ids = {u.id for u in user.following}
    
    return templates.TemplateResponse(
        request,
        "pages/connections.html",
        {
            "user": user,
            "following": user.following,
            "followers": user.followers,
            "following_ids": following_ids,
        }
    )


@user_router.post("/users/{user_id}/follow", include_in_schema=False)
async def toggle_follow(
    user_id: int,
    request: Request,
    db: DBSession
):
    current_user = request.state.user
    if not current_user:
        raise AuthenticationException("Not authenticated")
        
    if current_user.id == user_id:
        raise APPException(status_code=400, message="You cannot follow yourself.")
        
    user_service = UserService(db)
    target_user = await user_service.get(user_id)
    if not target_user:
        raise NotFoundException(message=f"User with the id: {user_id} doesn't exist!")
        
    # Re-fetch current_user with following loaded to avoid lazy load issues
    res = await db.scalars(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.following))
    )
    current_user_loaded = res.unique().one()
    
    # Re-fetch target_user with followers loaded
    res_target = await db.scalars(
        select(User)
        .where(User.id == target_user.id)
        .options(selectinload(User.followers))
    )
    target_user_loaded = res_target.unique().one()

    is_following = False
    if target_user_loaded in current_user_loaded.following:
        current_user_loaded.following.remove(target_user_loaded)
    else:
        current_user_loaded.following.append(target_user_loaded)
        is_following = True
        
    await db.commit()
    
    return {
        "success": True,
        "following": is_following,
        "followers_count": len(target_user_loaded.followers)
    }
