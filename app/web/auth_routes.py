from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import async_get_db
from app.models.models import User
from app.services.user_service import UserService
from app.utils.auth import create_user_token, hash_password
from app.utils.exceptions import ConflictException, AuthenticationException

auth_router = APIRouter()
DBSession = Annotated[AsyncSession, Depends(async_get_db)]

class WebLoginRequest(BaseModel):
    username: str
    password: str

class WebRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

@auth_router.post("/login")
async def web_login(
    login_data: WebLoginRequest,
    response: Response,
    db: DBSession
):
    try:
        user_service = UserService(db)
        user = await user_service.authenticate_user(login_data)
        
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        user_token = create_user_token(token_data)
        
        # Set access_token cookie
        response.set_cookie(
            key="access_token",
            value=user_token,
            httponly=True,
            max_age=1800,  # 30 mins
            samesite="lax",
            secure=False,  # Set True in production
        )
        return {"success": True, "message": "Logged in successfully"}
    except AuthenticationException as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": e.message}
        )

@auth_router.post("/register")
async def web_register(
    register_data: WebRegisterRequest,
    response: Response,
    db: DBSession
):
    try:
        user_service = UserService(db)
        
        await user_service.validate_unique_user(
            username=register_data.username,
            email=register_data.email
        )
        
        new_user = User(
            username=register_data.username,
            email=register_data.email.lower(),
            password_hash=hash_password(register_data.password)
        )
        
        user = await user_service.add(new_user)
        
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        user_token = create_user_token(token_data)
        
        response.set_cookie(
            key="access_token",
            value=user_token,
            httponly=True,
            max_age=1800,
            samesite="lax",
            secure=False,
        )
        return {"success": True, "message": "Registered successfully"}
    except ConflictException as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"success": False, "message": e.message}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": str(e)}
        )

@auth_router.get("/logout")
async def web_logout():
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
