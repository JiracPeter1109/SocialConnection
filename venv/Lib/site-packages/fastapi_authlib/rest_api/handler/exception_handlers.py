"""
Customs FastAPI exception handlers

Handle customs exception, and return some http status_code.
"""
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi_authlib.utils.exceptions import (AuthenticationError,
                                              ObjectDoesNotExist, OIDCError)


async def fastapi_oidc_exception_handler(request: Request, ex: OIDCError):
    """
    Handle OIDCError with http code 500
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': ex.detail}
    )


async def authentication_error_handler(request: Request, ex: AuthenticationError):
    """
    Handle AuthenticationError with http code 401
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': ex.detail}
    )


async def object_does_not_exist_handler(request: Request, ex: ObjectDoesNotExist):
    """
    Handle ObjectDoesNotExist with http code 404
    :param request:
    :param ex:
    :return:
    """
    _ = request
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': ex.detail}
    )
