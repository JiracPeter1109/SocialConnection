"""
middleware
"""
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response

from fastapi_sa.database import session_ctx


class DBSessionMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """
    DBSessionMiddleware
    """

    @session_ctx
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        return await call_next(request)
