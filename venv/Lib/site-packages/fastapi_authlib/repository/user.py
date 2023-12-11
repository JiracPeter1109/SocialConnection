"""User"""
from sqlalchemy import select

from fastapi_authlib.models import User
from fastapi_authlib.repository.base import BaseRepository
from fastapi_authlib.schemas.user import UserCreate, UserSchema, UserUpdate
from fastapi_authlib.utils.exceptions import ObjectDoesNotExist


class UserRepository(BaseRepository[User, UserCreate, UserUpdate, UserSchema]):
    """
    User repository
    """
    model = User
    model_schema = UserSchema

    async def get_by_email(self, email: str) -> UserSchema:
        """Get by email"""
        stmt = select(User).filter(User.email == email)
        user: User = await self.session.scalar(stmt)
        if not user:
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(user)
