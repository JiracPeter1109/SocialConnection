"""Utils"""

import datetime
from typing import Optional, Tuple

import jwt

from fastapi_authlib.schemas.token import TokenSchema


def get_authorization_scheme_param(
    authorization_header_value: Optional[str],
) -> Tuple[str, str]:
    """
    Get authorization scheme param
    """
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


def get_utc_timestamp(**kwargs) -> int:
    """
    Get utc timestamp
    :param kwargs: timedelta parameters, example:  days=0 or hours=-1
    :return:
    """
    timedelta_kwargs = {key: value for key, value in kwargs.items() if value != 0}
    utc_time = datetime.datetime.utcnow()
    if timedelta_kwargs:
        utc_time += datetime.timedelta(**timedelta_kwargs)
    return int(utc_time.timestamp())


def encode_token(payload: dict, secret_key: str, algorithm: str) -> str:
    """
    Encode token
    :param payload:
    :param secret_key:
    :param algorithm:
    :return:
    """
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorithm: str) -> TokenSchema:
    """
    Decode token
    :param token:
    :param secret_key:
    :param algorithm:
    :return:
    """
    user = jwt.decode(token, secret_key, algorithms=[algorithm])
    return TokenSchema(**user)
