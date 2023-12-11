"""Group"""
from sqlalchemy import select

from fastapi_authlib.models import GroupUserMap
from fastapi_authlib.repository.base import BaseRepository
from fastapi_authlib.schemas.group_user_map import (GroupUserMapCreate,
                                                    GroupUserMapSchema,
                                                    GroupUserMapUpdate)


class GroupUserMapRepository(BaseRepository[GroupUserMap, GroupUserMapCreate, GroupUserMapUpdate, GroupUserMapSchema]):
    """
    GroupUserMap repository
    """
    model = GroupUserMap
    model_schema = GroupUserMapSchema

    async def get_by_user_id(self, user_id: int) -> list[GroupUserMapSchema]:
        """Get GroupUserMap by user_id"""
        stmt = select(GroupUserMap).filter(GroupUserMap.user_id == user_id)
        group_users: list[GroupUserMap] = await self.session.scalars(stmt)
        return [self.model_schema.from_orm(group_user) for group_user in group_users]
