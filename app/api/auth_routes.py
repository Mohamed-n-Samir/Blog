from typing import Annotated

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import  User
from app.models.schemas import UserResponse, UserCreate

from app.services.user_service import UserService

from app.utils.exceptions import NotFoundException

from app.config.database import async_get_db

DBSession = Annotated[AsyncSession, Depends(async_get_db)]
auth_router = APIRouter()


# Users
@auth_router.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: DBSession):

    user_service = UserService(db)

    user = await user_service.get(id=user_id)

    if user:
        return user
    raise NotFoundException(f"User with the id: {user_id} doesn't exist!")


@auth_router.post(
    "/api/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(new_user: UserCreate, db: DBSession):

    user_service = UserService(db)
    
    await user_service.validate_unique_user(username=new_user.username, email=new_user.email)

    new_user = User(**(new_user.model_dump()))

    committed_user = await user_service.add(new_user)

    return committed_user