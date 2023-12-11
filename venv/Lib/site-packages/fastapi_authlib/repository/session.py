"""Session"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fastapi_authlib.models import Session, User
from fastapi_authlib.repository.base import BaseRepository
from fastapi_authlib.schemas.session import (SessionCreate, SessionSchema,
                                             SessionUpdate)
from fastapi_authlib.utils.exceptions import ObjectDoesNotExist


class SessionRepository(BaseRepository[Session, SessionCreate, SessionUpdate, SessionSchema]):
    """
    Session repository
    """
    model = Session
    model_schema = SessionSchema

    async def get_session_from_user_id(self, user_id: int) -> SessionSchema:
        """
        Get session from user id
        :param user_id:
        :return:
        """

        stmt = select(User).filter(User.id == user_id).options(selectinload(User.session))
        user: User = await self.session.scalar(stmt)
        if not user:
            raise ObjectDoesNotExist()
        if not user.session:
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(user.session[0])
