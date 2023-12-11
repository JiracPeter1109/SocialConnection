"""OIDC"""
import threading
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import Depends, FastAPI
from starlette.middleware.sessions import SessionMiddleware

from fastapi_authlib.config import settings
from fastapi_authlib.rest_api.handler import init_exception_handler
from fastapi_authlib.rest_api.routers import login, logout, user
from fastapi_authlib.utils.auth_dependency import check_auth_depends


class OIDCClient:
    """OIDC"""

    def __init__(
        self,
        app: FastAPI,
        oauth_client_id: str,
        oauth_client_secret: str,
        oauth_conf_url: str,
        database: str,
        secret_key: str,
        algorithm: str = 'HS256',
        platform: str = 'default',
        router_prefix: str = '',
        exp_period: int = 30,
        nts_period: int = 10,
    ) -> None:
        """
        Init OIDC basic configuration
        :param app: fastapi object
        :param oauth_client_id: oidc client id
        :param oauth_client_secret:
        :param oauth_conf_url:
        :param database:
        :param secret_key: jwt secret key
        :param algorithm: jwt algorithm, default: HS256
        :param platform:
        :param router_prefix:
        :param exp_period: jwt token expiration duration, unit: day
        :param nts_period: jwt token refresh duration: unit: minute
        """

        if not database:
            raise TypeError('Missing Database parameters, it is required')

        if not all([oauth_client_id, oauth_client_secret, oauth_conf_url]):
            raise TypeError('Missing Oauth parameters, it is required')

        if not app:
            raise TypeError('Missing App parameters, it is required')

        if not secret_key:
            raise TypeError('Missing SECRET_KEY parameters, it is required')

        settings.DATABASE = database
        settings.OAUTH_CLIENT_ID = oauth_client_id
        settings.OAUTH_CLIENT_SECRET = oauth_client_secret
        settings.OAUTH_CONF_URL = oauth_conf_url
        settings.SECRET_KEY = secret_key
        settings.PLATFORM = platform
        settings.ALGORITHM = algorithm
        settings.EXP_PERIOD = exp_period
        settings.NTS_PERIOD = nts_period
        self.app = app
        self.route_prefix = router_prefix

    @staticmethod
    def migrate_db():
        """
        Migrates the database
        :return:
        """
        alembic_cfg = Config(Path(Path(__file__).parent, 'alembic/alembic.ini'))
        alembic_cfg.set_main_option("script_location", "fastapi_authlib:alembic")
        command.upgrade(alembic_cfg, 'head')

    def init_app(self):
        """
        Init app
        :return:
        """
        # init handle
        init_exception_handler(self.app)

        # init route
        self.app.include_router(
            login.router,
            tags=['login'],
            prefix=self.route_prefix
        )

        self.app.include_router(
            logout.router,
            tags=['logout'],
            prefix=self.route_prefix,
            dependencies=[Depends(check_auth_depends)]
        )
        self.app.include_router(
            user.router,
            tags=['user'],
            prefix=self.route_prefix,
            dependencies=[Depends(check_auth_depends)]
        )

        self.app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    def init_oidc(self):
        """Init oidc"""
        thread = threading.Thread(target=self.migrate_db)
        thread.start()
        self.init_app()
