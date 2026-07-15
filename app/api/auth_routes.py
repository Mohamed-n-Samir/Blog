from typing import Annotated

from fastapi import APIRouter, Depends, status

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import  User
from app.models.schemas import Token, UserPrivateResponse, UserCreate

from app.services.user_service import UserService

from app.utils.auth import create_user_token, oauth2_scheme, verify_user_token
from app.utils.exceptions import AuthenticationException, NotFoundException

from app.config.database import async_get_db

DBSession = Annotated[AsyncSession, Depends(async_get_db)]
auth_router = APIRouter()


@auth_router.post("/api/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data)

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value
    }

    user_token = create_user_token(token_data)

    return Token(access_token=user_token, token_type="bearer")


@auth_router.post("/api/me", response_model=UserPrivateResponse)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
):
    user_service = UserService(db)
    payload = verify_user_token(token)

    user_id = payload.get("sub")


    if user_id is None:
        raise AuthenticationException(message="Invalid or expired token")
    
    user = await user_service.get(user_id=user_id)

    if not user:
        raise AuthenticationException(message="User Not found")
    
    return user




