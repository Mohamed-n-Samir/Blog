from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_username(self, username: str) -> User | None:
        return (
            await self.db.execute(
                select(User).where(User.username == username)
            )
        ).scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        return (
            await self.db.execute(
                select(User).where(User.email == email)
            )
        ).scalar_one_or_none()