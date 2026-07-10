from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.tag_repository import TagRepository

from app.models.models import Tag

from app.utils.exceptions import ConflictException

import logging

logger = logging.getLogger(__name__)

class TagService:
    def __init__(self, db: AsyncSession):
        self.repo = TagRepository(db)

    async def get_by_name(self, name: str):
        return await self.repo.get_by(name=name)
    
    async def get_all(self):
        return await self.repo.get_all()
    
    async def add(self, tag: Tag):

        try:
            tag = await self.repo.add(tag)
            await self.repo.db.commit()
            return tag
        except IntegrityError as e:
            await self.repo.db.rollback()
            logger.error("Error while trying to save the new tag", e)
            raise ConflictException(f"Tag already exists, {e._message}")
    
    async def add_all(self, tags: list[Tag]):
        try:
            tags = await self.repo.add_all(tags)
            await self.repo.db.commit()
            return tags
        except IntegrityError as e:
            await self.repo.db.rollback()
            logger.error("Error while trying to save the new tag", e)
            raise ConflictException(f"Tag already exists, {e._message}")