from contextlib import asynccontextmanager

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

from app.config.database import Base, engine, create_tables, close_db_connections

from app.constants.constant import ROOT_DIR
from app.config.settings import settings

from app.web.home import home_router

from typing import Annotated




# app = FastAPI()

# App lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting FastAPI Production Template...")
    if settings.environment == "development":
        await create_tables()  # Uncomment when database is set up
    print(f"✅ Server running on {settings.host}:{settings.port} (Database disabled for demo)")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down server...")
    await close_db_connections()  # Uncomment when database is set up
    print("✅ Server shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="FastAPI Blog",
    description="A comprehensive, production-ready FastAPI Blog template for Blog management with authentication, categories, priorities, and analytics",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)


if settings.app_mode in ["full", 'web']: 
    app.mount("/static", StaticFiles(directory=ROOT_DIR / "static"), name="static")
    app.mount("/media", StaticFiles(directory=ROOT_DIR / "media"), name="media")


app.include_router(router=home_router)







# # Server API
# # GETS
# # Users
# @app.get("/api/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
#     result = db.execute(select(models.User).where(models.User.id == user_id))
#     user = result.scalar_one_or_none()

#     if user:
#         return user
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"User with the id: {user_id} doesn't exist!",
#     )


# # User Posts
# @app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
# def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
#     result = db.execute(select(models.User).where(models.User.id == user_id))
#     user = result.scalar_one_or_none()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with the id: {user_id} doesn't exist!",
#         )

#     result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
#     posts = result.scalars().all()
#     return posts


# # POSTS
# # Users
# @app.post(
#     "/api/users",
#     status_code=status.HTTP_201_CREATED,
#     response_model=UserResponse,
# )
# def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
#     existing_user = db.execute(
#         select(models.User).where(
#             or_(
#                 models.User.username == user.username,
#                 models.User.email == user.email,
#             )
#         )
#     ).scalar_one_or_none()

#     if existing_user:
#         field = "Username" if existing_user.username == user.username else "Email"

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"{field} already exists",
#         )

#     new_user = models.User(**(user.model_dump()))

#     db.add(new_user)

#     try:
#         db.commit()
#         db.refresh(new_user)
#         return new_user

#     except IntegrityError as e:
#         db.rollback()

#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"User already exists, {e._message}",
#         )


# # Posts
# @app.post(
#     "/api/posts",
#     status_code=status.HTTP_201_CREATED,
#     response_model=PostResponse,
# )
# def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):

#     user = db.execute(
#         select(models.User).where(models.User.id == post.user_id)
#     ).scalar_one_or_none()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=" User doesn't exists",
#         )

#     new_post = models.Post(**(post.model_dump()))

#     db.add(new_post)

#     db.commit()
#     db.refresh(new_post)
#     return new_post



# # Exceptions
# @app.exception_handler(status.HTTP_404_NOT_FOUND)
# def not_found(request: Request, exc: HTTPException):
#     message = (
#         exc.detail
#         if exc.detail
#         else "The page you're looking for doesn't exist or has been moved."
#     )

#     if request.url.path.startswith("/api"):
#         return JSONResponse(
#             status_code=exc.status_code,
#             content={"detail": message},
#         )

#     return templates.TemplateResponse(
#         request=request,
#         name="errors/404.html",
#         context={"message": message},
#         status_code=status.HTTP_404_NOT_FOUND,
#     )


# @app.exception_handler(StarletteHTTPException)
# def handle_exceptions(request: Request, exc: StarletteHTTPException):
#     message = (
#         exc.detail
#         if exc.detail
#         else "An error occurred. Please check your request and try again."
#     )
#     if request.url.path.startswith("/api"):
#         return JSONResponse(
#             status_code=exc.status_code,
#             content={"detail": message},
#         )

#     return templates.TemplateResponse(
#         request=request,
#         name="errors/error.html",
#         context={"message": message, "status_code": exc.status_code},
#         status_code=exc.status_code,
#     )


# @app.exception_handler(RequestValidationError)
# def handle_validation_errors(request: Request, exc: RequestValidationError):
#     if request.url.path.startswith("/api"):
#         return JSONResponse(
#             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
#             content={"detail": exc.errors()},
#         )

#     error_msg = "Invalid request. Please check your input and try again."

#     return templates.TemplateResponse(
#         request=request,
#         name="errors/error.html",
#         context={
#             "message": error_msg,
#             "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
#         },
#         status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
#     )
