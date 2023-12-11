"""user"""
from typing import Optional

from fastapi_authlib.messages.base import Message
from fastapi_authlib.schemas.user import UserSchema


class UserMessage(Message):
    """User message"""
    data: Optional[UserSchema]
