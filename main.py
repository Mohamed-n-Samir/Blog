from fastapi import Depends, Body, FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models import models
from app.models.schemas import PostCreate, PostResponse, UserCreate, UserResponse

from app.config.database import Base, engine, get_db

from pathlib import Path
from typing import Annotated

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)


app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


# Client pages
@app.get("/", include_in_schema=False, name="root")
@app.get("/blog", include_in_schema=False, name="blog")
def home_page(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(request, "pages/index.html", {"posts": posts})


@app.get("/blog/posts/{post_id}", include_in_schema=False, name="post")
def post_page(post_id: int, request: Request, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    print("after_resut")
    post = result.scalar_one_or_none()
    if post:
        return templates.TemplateResponse(request, "pages/post.html", {"post": post})

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not found")


@app.get(
    "/users/{user_id}/posts", include_in_schema=False, response_model=list[PostResponse]
)
def get_user_posts(user_id: int, request: Request,db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the id: {user_id} doesn't exist!",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()

    return templates.TemplateResponse(request, "pages/user_posts.html", {"posts": posts, 'user': user})


@app.get("/categories", include_in_schema=False, name="categories")
def categories(request: Request):
    return templates.TemplateResponse(request, "pages/categories.html")


# Server API
# GETS
# Users
@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with the id: {user_id} doesn't exist!",
    )


# User Posts
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the id: {user_id} doesn't exist!",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts


# POSTS
# Users
@app.post(
    "/api/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(
        select(models.User).where(
            or_(
                models.User.username == user.username,
                models.User.email == user.email,
            )
        )
    ).scalar_one_or_none()

    if existing_user:
        field = "Username" if existing_user.username == user.username else "Email"

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{field} already exists",
        )

    new_user = models.User(**(user.model_dump()))

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
        return new_user

    except IntegrityError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already exists, {e._message}",
        )


# Posts
@app.post(
    "/api/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=PostResponse,
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):

    user = db.execute(
        select(models.User).where(models.User.id == post.user_id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=" User doesn't exists",
        )

    new_post = models.Post(**(post.model_dump()))

    db.add(new_post)

    db.commit()
    db.refresh(new_post)
    return new_post



# Exceptions
@app.exception_handler(status.HTTP_404_NOT_FOUND)
def not_found(request: Request, exc: HTTPException):
    message = (
        exc.detail
        if exc.detail
        else "The page you're looking for doesn't exist or has been moved."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        context={"message": message},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.exception_handler(StarletteHTTPException)
def handle_exceptions(request: Request, exc: StarletteHTTPException):
    message = (
        exc.detail
        if exc.detail
        else "An error occurred. Please check your request and try again."
    )
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request=request,
        name="errors/error.html",
        context={"message": message, "status_code": exc.status_code},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
def handle_validation_errors(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exc.errors()},
        )

    error_msg = "Invalid request. Please check your input and try again."

    return templates.TemplateResponse(
        request=request,
        name="errors/error.html",
        context={
            "message": error_msg,
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
