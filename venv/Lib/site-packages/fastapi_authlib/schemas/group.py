"""
Group schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from fastapi_authlib.schemas.base import InDBMixin


class GroupBase(BaseModel):
    """Group base schema."""
    name: constr(max_length=100) = None


class GroupSchema(GroupBase, InDBMixin):
    """Group model schema."""


class GroupCreate(GroupBase):
    """Group create schema."""
    name: constr(max_length=100)


class GroupUpdate(GroupBase):
    """Group update schema."""
