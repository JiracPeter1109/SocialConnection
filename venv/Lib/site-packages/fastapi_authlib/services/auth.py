"""auth"""
import logging

from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

from fastapi_authlib.config import settings
from fastapi_authlib.models import User
from fastapi_authlib.repository.group import GroupRepository
from fastapi_authlib.repository.group_user_map import GroupUserMapRepository
from fastapi_authlib.repository.session import SessionRepository
from fastapi_authlib.repository.user import UserRepository
from fastapi_authlib.schemas.group import GroupCreate
from fastapi_authlib.schemas.group_user_map import GroupUserMapCreate
from fastapi_authlib.schemas.session import SessionCreate, SessionUpdate
from fastapi_authlib.schemas.token import TokenSchema
from fastapi_authlib.schemas.user import UserCreate, UserSchema, UserUpdate
from fastapi_authlib.services.base import EntityService
from fastapi_authlib.utils import get_utc_timestamp
from fastapi_authlib.utils.exceptions import (AuthenticationError,
                                              ObjectDoesNotExist, OIDCError)

logger = logging.getLogger(__name__)


class AuthService(EntityService[User, UserCreate, UserUpdate, UserSchema]):
    """
    Auth service.
    """
    REPOSITORY_CLASS = UserRepository

    def __init__(self):
        self.oauth_client = OAuth(settings)
        self.register_oauth()
        self.exp_period = settings.EXP_PERIOD
        self.nts_period = settings.NTS_PERIOD

    @property
    def session_repository(self):
        """Session repository"""
        return SessionRepository()

    @property
    def group_repository(self):
        """Group repository"""
        return GroupRepository()

    @property
    def group_user_map_repository(self):
        """Group user map repository"""
        return GroupUserMapRepository()

    def register_oauth(self):
        """Register OAuth"""
        self.oauth_client.register(
            name='oauth',
            server_metadata_url=settings.OAUTH_CONF_URL,
            client_kwargs={
                'scope': 'openid email profile',
                'verify': False
            }
        )

    async def login(self, request: Request, redirect_uri: str):
        """
        Login
        :param request:
        :param redirect_uri:
        :return:
        """
        return await self.oauth_client.oauth.authorize_redirect(request, redirect_uri)

    async def logout(self, user_id: int):
        """
        Logout
        :param user_id:
        :return:
        """
        # 清除数据库中的对应数据
        try:
            await self.clear_token_info(pk=user_id)
        except ObjectDoesNotExist:
            logger.warning('User does not exist')

    async def auth(self, request: Request, **_) -> dict:
        """
        Auth
        :param request:
        :param _:
        :return:
        """
        try:
            token = await self.oauth_client.oauth.authorize_access_token(request)
        except OAuthError as ex:
            logger.error('OAuth Error, exception info: %s', ex)
            raise OIDCError('OAuth Error') from ex
        userinfo = token.get('userinfo')

        # the email is unique
        try:
            user = await self.repository.get_by_email(userinfo.email)
            active = user.active
            user_obj_in = UserUpdate(
                name=userinfo.name,
                nickname=userinfo.nickname,
                picture=userinfo.picture,
                active=True
            )
            user = await self.repository.update_by_id(pk=user.id, obj_in=user_obj_in)
            if active:
                session = await self.session_repository.get_session_from_user_id(user.id)
                await self.session_repository.delete_by_id(session.id)

        except ObjectDoesNotExist:
            user_obj_in = UserCreate(
                name=userinfo.name,
                nickname=userinfo.nickname,
                email=userinfo.email,
                email_verified=userinfo.email_verified,
                picture=userinfo.picture,
                active=True,
            )
            user = await self.repository.create(obj_in=user_obj_in)

        session_obj_in = SessionCreate(user_id=user.id, platform_name=settings.PLATFORM, **token)
        await self.session_repository.create(obj_in=session_obj_in)
        groups = userinfo.get('groups_direct')
        await self.save_group_and_group_user_map(groups, user)

        payload = self.format_payload(user)
        return payload

    async def get_user_by_id(self, pk: int) -> UserSchema:
        """
        Get user by id
        :param pk:
        :return:
        """
        user = await self.repository.get_by_id(pk)
        if not user.active:
            raise AuthenticationError()
        return user

    async def clear_token_info(self, pk: int):
        """
        Clear token info
        :param pk:
        :return:
        """

        await self.clear_session_with_user_id(pk=pk)
        await self.repository.update_by_id(
            pk=pk,
            obj_in=UserUpdate(active=False)
        )

    async def clear_session_with_user_id(self, pk: int):
        """
        Clear session with user id
        :param pk:
        :return:
        """
        try:
            session = await self.session_repository.get_session_from_user_id(user_id=pk)
            return await self.session_repository.delete_by_id(session.id)
        except ObjectDoesNotExist:
            logger.warning('Session does not exist')

    async def save_group_and_group_user_map(self, groups: list, user: UserSchema) -> None:
        """
        Save group and group user map
        :param groups: group names
        :param user:
        :return:
        """
        group_ids = []
        for name in groups:
            try:
                group = await self.group_repository.get_by_name(name=name)
            except ObjectDoesNotExist:
                group = await self.group_repository.create(obj_in=GroupCreate(name=name))
            group_ids.append(group.id)

        try:
            exist_groups = await self.group_user_map_repository.get_by_user_id(user_id=user.id)
            # compare id
            exist_group_ids = [group.group_id for group in exist_groups]
            exist_group_map = {str(group.group_id): group.id for group in exist_groups}
            # delete id
            delete_ids = set(exist_group_ids) - set(group_ids)
            for group_id in delete_ids:
                await self.group_user_map_repository.delete_by_id(exist_group_map.get(str(group_id)))

            # insert id
            insert_ids = set(group_ids) - set(exist_group_ids)
            for group_id in insert_ids:
                await self.group_user_map_repository.create(
                    obj_in=GroupUserMapCreate(
                        group_id=group_id,
                        user_id=user.id
                    )
                )

        except ObjectDoesNotExist:
            for group_id in group_ids:
                await self.group_user_map_repository.create(
                    obj_in=GroupUserMapCreate(
                        group_id=group_id,
                        user_id=user.id
                    )
                )

    async def verify_user(self, pk: int) -> dict:
        """
        Verify user
        :param pk: user id
        :return:
        """
        # check user active
        user = await self.repository.get_by_id(pk)
        if not user.active:
            raise AuthenticationError()

        session = await self.session_repository.get_session_from_user_id(pk)
        # check token
        try:
            userinfo = await self.oauth_client.oauth.userinfo(token={'access_token': session.access_token})
        except Exception as ex:
            logger.debug(
                'Get userinfo with access_token of user %s error, try use refresh token, exception info: %s',
                pk,
                ex
            )
            try:
                # check refresh_token
                access_token = await self.oauth_client.oauth.fetch_access_token(
                    refresh_token=session.refresh_token,
                    grant_type='refresh_token'
                )
            except Exception as ex:
                logger.debug('Get access_token with refresh_token of user %s error', pk)
                await self.clear_token_info(pk=pk)
                raise AuthenticationError('Token expired error') from ex

            userinfo = await self.oauth_client.oauth.userinfo(token={'access_token': access_token})
            # save token
            await self.session_repository.update_by_id(
                pk=session.id,
                obj_in=SessionUpdate(**access_token)
            )
        # compare user and userinfo
        update_fields = {key: userinfo.get(key)
                         for key in ['name', 'nickname', 'picture']
                         if getattr(user, key) != userinfo.get(key)}
        if update_fields:
            user_obj_in = UserUpdate(**update_fields)
            user = await self.repository.update_by_id(pk=pk, obj_in=user_obj_in)

        # compare group map
        await self.save_group_and_group_user_map(groups=userinfo.get('groups'), user=user)

        payload = self.format_payload(user)
        return payload

    def format_payload(self, user: UserSchema) -> dict:
        """
        Format payload with user
        :param user:
        :return:
        """
        token_schema = TokenSchema(
            user_id=user.id,
            user_name=user.name,
            email=user.email,
            iat=get_utc_timestamp(),
            exp=get_utc_timestamp(days=self.exp_period),
            nst=get_utc_timestamp(minutes=self.nts_period)
        )
        return token_schema.dict()
