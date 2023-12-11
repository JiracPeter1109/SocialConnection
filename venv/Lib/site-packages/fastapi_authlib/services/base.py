"""
Base service.
"""
import logging
from typing import Any, Dict, Generic, Optional, Type, Union

from fastapi_authlib.repository.base import BaseRepository
from fastapi_authlib.utils.types import (CreateSchemaType, ModelSchemaType,
                                         ModelType, UpdateSchemaType)

logger = logging.getLogger(__name__)


class ICRUD:  # noqa
    """
    定义接口规范。
    """

    async def get(self, *args, **kwargs) -> Any:
        """
        查询记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def create(self, *args, **kwargs) -> Any:
        """
        创建记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def update(self, *args, **kwargs) -> Any:
        """
        更新记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    async def delete(self, *args, **kwargs) -> Any:
        """
        删除记录。

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError


class EntityService(ICRUD, Generic[ModelType, CreateSchemaType, UpdateSchemaType, ModelSchemaType]):
    """Base service."""
    REPOSITORY_CLASS: Type[BaseRepository]

    @property
    def repository(self):
        """repository"""
        return self.REPOSITORY_CLASS()

    async def get_by_id(self, pk: int) -> ModelSchemaType:
        """Get record by primary key."""
        return await self.repository.get_by_id(pk)

    async def get(
        self,
        *,
        sorting_fields: Optional[Union[set[str], list[str]]] = None,
        search_fields: Optional[dict[str, Any]] = None,
        limit: int = 5,
        offset: int = 0,
        **kwargs
    ) -> list[ModelSchemaType]:
        """
        Get multi record.
        :param sorting_fields:
        :param search_fields:
        :param limit:
        :param offset:
        :return:
        """
        return await self.repository.get(
            sorting_fields=sorting_fields,
            search_fields=search_fields,
            limit=limit,
            offset=offset,
        )

    async def create(
        self,
        *,
        obj_in: CreateSchemaType
    ) -> ModelSchemaType:
        """
        Create a record.
        :param obj_in:
        :return:
        """
        return await self.repository.create(obj_in=obj_in)

    async def update_by_id(
        self,
        pk: int,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelSchemaType:
        """
        Update a record.
        :param pk:
        :param obj_in:
        :return:
        """
        return await self.repository.update_by_id(pk=pk, obj_in=obj_in)

    async def update(
        self,
        pk: int,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelSchemaType:
        """
        Update a record
        :param pk:
        :param obj_in:
        :return:
        """
        return await self.update_by_id(pk=pk, obj_in=obj_in)

    async def delete_by_id(self, *, pk: int) -> ModelSchemaType:
        """
        Delete a record by primary key.
        :param pk:
        :return:
        """
        return await self.repository.delete_by_id(pk)

    async def delete(self, *, pk: int) -> ModelSchemaType:
        """
        Delete a record
        :param pk:
        :return:
        """
        return await self.delete_by_id(pk=pk)

    async def count(self, search_fields: dict[str, str] = None) -> int:
        """
        Count.
        :return:
        """
        return await self.repository.count(search_fields)
