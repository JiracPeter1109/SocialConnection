"""
Base schema.
"""
from datetime import datetime

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class InDBMixin(BaseModel):
    """Db model mixin."""
    id: int
    update_time: datetime = None
    create_time: datetime = None

    class Config:
        """Model ORM config"""
        orm_mode = True
        arbitrary_types_allowed = True
