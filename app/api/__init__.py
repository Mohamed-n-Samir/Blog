from fastapi import APIRouter

from app.api.user_routes import user_router
from app.api.post_routes import post_router
from app.api.tag_routes import tag_router
from app.api.upload_routes import upload_router

api_router = APIRouter()

api_router.include_router(user_router, tags=["Users"])
api_router.include_router(post_router, tags=["Posts"])
api_router.include_router(tag_router, tags=["Tags"])
api_router.include_router(upload_router, tags=["Upload"])
