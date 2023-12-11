"""
Exceptions.
"""
from typing import Optional


class OIDCError(Exception):
    """OIDCError"""

    def __init__(self, detail: str):
        """
        :param detail:
        """
        self.detail = detail
        super().__init__(detail)

    def __repr__(self):
        """repr"""
        return f'{self.__class__.__name__}("detail"={self.detail})'


class AuthenticationError(OIDCError):
    """
    Authentication error.

    http code: 401
    """

    def __init__(
        self,
        detail: Optional[str] = 'Authentication failed!',
    ):
        super().__init__(detail)


class ObjectDoesNotExist(OIDCError):
    """
    Object does not exist.

    http code: 404
    """

    def __init__(
        self,
        detail: Optional[str] = 'Object does not exist!',
    ):
        super().__init__(detail)
