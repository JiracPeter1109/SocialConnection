"""
Exceptions
"""


class FastAPISQLAlchemyError(Exception):
    """FastAPI SQLAlchemy error"""


class SQLAlchemyNotInitError(FastAPISQLAlchemyError):
    """
    SALAlchemy Not init Error
    """
    msg = """
    SQLAlchemy not init, please init first.
    eg:
    db = SQLAlchemy('sqlite+aiosqlite://')
    db.init()
    """

    def __init__(self):
        super().__init__(self.msg)
