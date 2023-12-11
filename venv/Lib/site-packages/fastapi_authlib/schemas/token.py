"""Token schema"""

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module


class TokenSchema(BaseModel):
    """token schema."""
    user_id: int
    user_name: constr(max_length=100)
    email: constr(max_length=200)
    iat: int
    exp: int
    nst: int

    class Config:
        """Model ORM config"""
        orm_mode = False
        arbitrary_types_allowed = True
