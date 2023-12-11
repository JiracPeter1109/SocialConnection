"""
Group User map schema
"""
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from fastapi_authlib.schemas.base import InDBMixin


class GroupUserMapBase(BaseModel):
    """Group User map base schema."""
    user_id: int = 0
    group_id: int = 0


class GroupUserMapSchema(GroupUserMapBase, InDBMixin):
    """Group User map model schema."""


class GroupUserMapCreate(GroupUserMapBase):
    """Group User map create schema."""
    user_id: int
    group_id: int


class GroupUserMapUpdate(GroupUserMapBase):
    """Group User map update schema."""
