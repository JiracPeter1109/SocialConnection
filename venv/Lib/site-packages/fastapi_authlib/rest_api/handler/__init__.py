"""
FastAPI handler
"""
from fastapi import FastAPI

from fastapi_authlib.rest_api.handler import exception_handlers as exh
from fastapi_authlib.utils import exceptions as exs


def init_exception_handler(app: FastAPI):
    """
    Init exception handler.
    :param app:
    :return:
    """
    # 多对应关系
    exceptions = [
        exs.OIDCError,
        exs.AuthenticationError,
        exs.ObjectDoesNotExist,
    ]

    handler_exceptions = [
        exh.fastapi_oidc_exception_handler,
        exh.authentication_error_handler,
        exh.object_does_not_exist_handler,
    ]

    for k, v in dict(zip(exceptions, handler_exceptions)).items():
        app.add_exception_handler(
            exc_class_or_status_code=k,
            handler=v
        )
