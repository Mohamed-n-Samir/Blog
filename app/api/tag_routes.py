from typing import Annotated

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload 

from app.models.models import Tag
from app.models.schemas import TagResponse, TagCreate

from app.services.tag_service import TagService

from app.utils.exceptions import NotFoundException

from app.config.database import async_get_db


DBSession = Annotated[AsyncSession, Depends(async_get_db)]
tag_router = APIRouter()


@tag_router.get("/api/tags", response_model=list[TagResponse])
async def get_tags( db:DBSession):
    tag_service = TagService(db)

    return await tag_service.get_all()


@tag_router.get("/api/tags/{name}", response_model=list[TagResponse])
async def get_tags(name: str, db:DBSession):
    tag_service = TagService(db)

    tag = await tag_service.get_by_name(name=name)

    if not tag:
        raise NotFoundException(message=f"The tag with name: {name} Not found")

    return tag

@tag_router.post(
    "/api/tags",
    status_code=status.HTTP_201_CREATED,
    response_model=list[TagResponse],
)
async def create_tag(tags: list[TagCreate], db: DBSession):

    tag_service = TagService(db)

    new_tags = [Tag(**(tag.model_dump())) for tag in tags]

    created_tags = await tag_service.add_all(new_tags)

    return created_tags


