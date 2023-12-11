"""base"""

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class BaseMessage(BaseModel):
    """Base Message"""
    message: str = 'ok'


class Message(BaseMessage):
    """Message"""
