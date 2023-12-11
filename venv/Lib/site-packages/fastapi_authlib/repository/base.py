"""
base repository
"""
from typing import Any, Generic, Optional, Type, Union

from fastapi.encoders import jsonable_encoder
from fastapi_sa.database import db
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from fastapi_authlib.utils.exceptions import ObjectDoesNotExist
from fastapi_authlib.utils.types import (CreateSchemaType, ModelSchemaType,
                                         ModelType, UpdateSchemaType)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ModelSchemaType]):
    """
    Base repository
    """
    model: Type[ModelType]
    model_schema: Type[ModelSchemaType]

    @property
    def session(self) -> AsyncSession:
        """local session"""
        return db.session

    async def get_by_id(self, pk: Any) -> ModelSchemaType:
        """
        Get one object by id
        :param pk:
        :return:
        """
        stmt = select(self.model).where(self.model.id == pk)
        obj = await self.session.scalar(stmt)
        if obj:
            return self.model_schema.from_orm(obj)
        raise ObjectDoesNotExist()

    async def get(
        self,
        *,
        sorting_fields: Optional[Union[set[str], list[str]]] = None,
        search_fields: Optional[dict[str, Any]] = None,
        limit: int = 5,
        offset: int = 0,
    ) -> list[ModelSchemaType]:
        """
        get
        """
        stmt = select(self.model)
        if sorting_fields:
            stmt = self._sort(stmt, sorting_fields)
        if search_fields:
            stmt = self._search(stmt, search_fields)
        stmt = self._paginate_by_limit_offset(stmt, limit, offset)
        objs = await self.session.execute(stmt)
        results = objs.scalars().all()
        if not results:
            raise ObjectDoesNotExist()
        return [self.model_schema.from_orm(obj) for obj in results]

    async def create(self, *, obj_in: CreateSchemaType) -> ModelSchemaType:
        """
        Create a object.
        :param obj_in:
        :return:
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        await self.session.flush()
        return self.model_schema.from_orm(db_obj)

    def _sort(self, stmt: Select, sorting_fields: Union[tuple[str], list[str]]) -> Select:
        """
        构造排序逻辑。
        :param stmt:
        :param sorting_fields:
        :return:
        """
        order_by_fields = []
        for field in sorting_fields:
            if field.startswith('-'):
                field = field[1:]
                table_field = getattr(self.model, field)
                order_by_fields.append(table_field.desc())
            else:
                table_field = getattr(self.model, field)
                order_by_fields.append(table_field.asc())
        return stmt.order_by(*order_by_fields)

    @staticmethod
    def _search(stmt: Select, search_fields: dict[str, str]) -> Select:
        """
        构造搜索逻辑.
        :param stmt:
        :param search_fields:
        :return:
        """
        return stmt.filter_by(**search_fields)

    @staticmethod
    def _paginate_by_limit_offset(stmt: Select, limit: int, offset: int) -> Select:
        """Page result by limit and offset"""
        return stmt.limit(limit).offset(offset)

    async def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, dict[str, Any]]
    ) -> ModelSchemaType:
        """
        Update a object.
        :param db_obj:
        :param obj_in:
        :return:
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        stmt = update(self.model).where(self.model.id == db_obj.id).values(**update_data)
        await self.session.execute(stmt)
        return self.model_schema.from_orm(db_obj)

    async def update_by_id(
        self,
        *,
        pk: int,
        obj_in: Union[UpdateSchemaType, dict[str, Any]]
    ) -> ModelSchemaType:
        """
        Update by id.
        :param pk:
        :param obj_in:
        :return:
        """
        obj = await self.get_by_id(pk)
        await self.update(db_obj=obj, obj_in=obj_in)
        return self.model_schema.from_orm(obj)

    async def delete(self, *, db_obj: ModelType) -> None:
        """
        Delete a object.
        :param db_obj:
        :return:
        """
        stmt = delete(self.model).where(self.model.id == db_obj.id)
        await self.session.execute(stmt)

    async def delete_by_id(self, pk: int) -> ModelSchemaType:
        """
        Delete object by id.
        :param pk:
        :return:
        """
        obj = await self.get_by_id(pk)
        await self.delete(db_obj=obj)
        return self.model_schema.from_orm(obj)

    async def count(self, search_fields: dict[str, str] = None) -> int:
        """
        Get total .
        :return:
        """
        stmt = select(func.count()).select_from(self.model)
        if search_fields:
            stmt = self._search(stmt, search_fields)
        return await self.session.scalar(stmt)
