"""
database
"""
import contextlib
import contextvars
import logging
from typing import cast

import sqlalchemy as sa
import sqlalchemy.orm  # pylint: disable=unused-import
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_sa.exceptions import SQLAlchemyNotInitError

logger = logging.getLogger(__name__)


class SingleMeta(type):
    """
    单例元类
    """
    __instance = None

    def __call__(cls, *args, **kwargs):
        if not cls.__instance:
            instance = super().__call__(*args, **kwargs)
            cls.__instances = instance
        return cls.__instances


class Database(metaclass=SingleMeta):
    """
    Database with Sqlalchemy

    usage:
        >>> db.init('sqlite+aiosqlite://')
    """

    def __init__(self):
        self.__engine: sa.ext.asyncio.engine.AsyncEngine | None = None
        self.__session_maker: sa.orm.sessionmaker | None = None
        self.__session_ctx: contextvars.ContextVar[
            sa.ext.asyncio.session.AsyncSession | None
            ] = contextvars.ContextVar("session_ctx", default=None)

    def init(
            self,
            url: str,
            echo: bool = False,
            engine_kw: dict = None,
            session_maker_kw: dict = None,
    ):
        """
        inti db
        :param url:
        :param echo:
        :param engine_kw:
        :param session_maker_kw:
        :return:
        """

        if engine_kw is None:
            engine_kw = {}
        if session_maker_kw is None:
            session_maker_kw = {}
        self.__engine = create_async_engine(
            url,
            echo=echo,
            future=True,
            **engine_kw
        )
        self.__session_maker = sa.orm.sessionmaker(
            self.engine,
            class_=sa.ext.asyncio.session.AsyncSession,
            # expire_on_commit=False,  # 取消提交后过期操作，此现象会产生缓存，请注意清理。
            **session_maker_kw
        )

    @property
    def session_ctx(self):
        """session context var"""
        return self.__session_ctx

    @property
    def session_maker(self):
        """sqlalchemy session maker"""
        if self.__session_maker:
            return self.__session_maker
        raise SQLAlchemyNotInitError

    @property
    def engine(self):
        """sqlalchemy engine"""
        if self.__engine:
            return self.__engine
        raise SQLAlchemyNotInitError

    @property
    def session(self) -> AsyncSession:
        """
        sqlalchemy session.

        You should call `db.init` first.
        :return:
        """
        assert self.session_maker
        _session = self.__session_ctx.get()
        if not _session:
            _session = self.session_maker()
        return _session

    def set_session_ctx(self):
        """set new session to ctx"""
        assert self.session_maker
        session = self.session_maker()
        session = cast(AsyncSession, session)
        logger.debug('Init context session, session: %s', session)
        token = self.session_ctx.set(session)
        logger.debug('Set session %s to context var, context var token: %s', session, token)
        return token

    def reset_session_ctx(self, token):
        """reset session ctx by token """
        self.session_ctx.reset(token)

    @contextlib.asynccontextmanager
    async def __call__(self, *args, **kwargs):
        token = self.set_session_ctx()
        session = self.__session_ctx.get()
        async with session.begin():
            yield session
        await session.close()
        self.reset_session_ctx(token)
        logger.debug('Reset session context var token: %s , session : %s', token, session)


db = Database()


def session_ctx(func: callable):
    """
    Session ctx with decorator

    usage:
        >>> @session_ctx
            async def foo():
                obj = await db.session.get(User, 1)
                assert obj.id == 1
    """

    async def _wrap(*args, **kwargs):
        async with db():
            result = await func(*args, **kwargs)
            return result

    return _wrap
