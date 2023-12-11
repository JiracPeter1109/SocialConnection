"""
Types.
"""
from typing import TypeVar

from pydantic import \
    BaseModel as SchemaModel  # pylint: disable=no-name-in-module

from fastapi_authlib.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=SchemaModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=SchemaModel)
ModelSchemaType = TypeVar('ModelSchemaType', bound=SchemaModel)
