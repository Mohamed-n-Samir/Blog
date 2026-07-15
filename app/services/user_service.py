from sqlalchemy import func, or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository

from app.models.models import User
from app.models.schemas import UserLogin

from app.utils.auth import verify_password
from app.utils.exceptions import AuthenticationException, ConflictException

import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get(self, user_id: int):
        return await self.repo.get(id=user_id)
    
    async def user_exists(self, user_id:int):
        return await self.repo.exists(id=user_id)
    
    async def add(self, user: User):
        try:
            user = await self.repo.add(user)
            await self.repo.db.commit()
            return user
        except IntegrityError as e:
            await self.repo.db.rollback()
            logger.error("Error while trying to save the new_user", e._message)
            raise ConflictException(f"User already exists, {e._message}")
        
    async def update(self, user: User) -> User:
        try:
            updated_user = await self.repo.update(user)
            await self.repo.db.commit()
            return updated_user
        except IntegrityError as e:
            await self.repo.db.rollback()
            logger.error("Error while trying to update user profile", e)
            raise ConflictException(f"Failed to update profile: {e._message}")
        
    async def validate_unique_user(
        self,
        *,
        username: str,
        email: str,
        exclude_user_id: int | None = None,
    ) -> None:
        conditions = [
            or_(
                func.lower(User.username) == username.lower(),
                func.lower(User.email) == email.lower(),
            )
        ]

        if exclude_user_id is not None:
            conditions.append(User.id != exclude_user_id)

        existing_user = await self.repo.find(
            and_(*conditions),
        )

        print(existing_user)

        if existing_user is None:
            return

        if existing_user.username == username:
            raise ConflictException("Username already exists")

        raise ConflictException("Email already exists")

        
    async def authenticate_user(self, user_data: UserLogin) -> User:
        user = await self.repo.get_by(email=user_data.username)
        
        if not user:
            raise AuthenticationException(message="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
        if not user.password_hash:
            raise AuthenticationException("Please login with your OAuth provider")
        if not verify_password(user_data.password, user.password_hash):
            raise AuthenticationException(message="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
            
        return user

