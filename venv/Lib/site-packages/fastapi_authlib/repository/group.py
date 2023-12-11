"""Group"""
from sqlalchemy import select

from fastapi_authlib.models import Group
from fastapi_authlib.repository.base import BaseRepository
from fastapi_authlib.schemas.group import GroupCreate, GroupSchema, GroupUpdate
from fastapi_authlib.utils.exceptions import ObjectDoesNotExist


class GroupRepository(BaseRepository[Group, GroupCreate, GroupUpdate, GroupSchema]):
    """
    Group repository
    """
    model = Group
    model_schema = GroupSchema

    async def get_by_name(self, name: str) -> GroupSchema:
        """Get by name"""
        stmt = select(Group).filter(Group.name == name)
        group: Group = await self.session.scalar(stmt)
        if not group:
            raise ObjectDoesNotExist()
        return self.model_schema.from_orm(group)
