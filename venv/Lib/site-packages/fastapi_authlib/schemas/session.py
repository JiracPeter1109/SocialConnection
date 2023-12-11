"""
Session schema
"""
from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

from fastapi_authlib.schemas.base import InDBMixin


class SessionBase(BaseModel):
    """Session base schema."""
    user_id: int = None
    platform_name: constr(max_length=40) = None
    token_type: constr(max_length=40) = None
    access_token: constr(max_length=200) = None
    refresh_token: constr(max_length=200) = None
    expires_at: int = None


class SessionSchema(SessionBase, InDBMixin):
    """Session model schema."""


class SessionCreate(SessionBase):
    """Session create schema."""
    user_id: int
    platform_name: constr(max_length=40)
    token_type: constr(max_length=40)
    access_token: constr(max_length=200)
    refresh_token: constr(max_length=200)
    expires_at: int


class SessionUpdate(SessionBase):
    """Session update schema."""
    access_token: constr(max_length=200)
    refresh_token: constr(max_length=200)
    expires_at: int
