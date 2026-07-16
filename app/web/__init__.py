from fastapi import APIRouter

from app.web.main_routes import main_router
from app.web.post_routes import post_router
from app.web.user_routes import user_router
from app.web.auth_routes import auth_router

web_router = APIRouter()

web_router.include_router(main_router)
web_router.include_router(post_router)
web_router.include_router(user_router)
web_router.include_router(auth_router)
