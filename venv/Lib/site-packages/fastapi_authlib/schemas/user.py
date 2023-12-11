"""
User schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from fastapi_authlib.schemas.base import InDBMixin


class UserBase(BaseModel):
    """User base schema."""
    name: constr(max_length=100) = None
    nickname: constr(max_length=100) = None
    email: constr(max_length=200) = None
    email_verified: bool = False
    picture: constr(max_length=1000) = None
    active: bool = False


class UserSchema(UserBase, InDBMixin):
    """User model schema."""


class UserCreate(UserBase):
    """User create schema."""
    name: constr(max_length=100)


class UserUpdate(UserBase):
    """User update schema."""
