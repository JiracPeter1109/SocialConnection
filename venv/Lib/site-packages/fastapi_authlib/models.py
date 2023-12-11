"""Model"""
from datetime import datetime

import inflection
from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, String)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship


class CustomBase:
    """
    Customs DB base class
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return inflection.underscore(cls.__name__)  # pylint: disable=no-member


BaseModel = declarative_base(cls=CustomBase)


class Group(BaseModel):
    """
    Group model
    """
    name = Column(String(100), nullable=False, comment='名称')

    group_map = relationship(
        'GroupUserMap',
        back_populates='group',
        passive_deletes=True
    )


class User(BaseModel):
    """
    User model
    """
    name = Column(String(100), nullable=False, comment='名称')
    nickname = Column(String(100), nullable=False, comment='别名')
    email = Column(String(200), nullable=False, comment='邮箱')
    email_verified = Column(Boolean, default=False, comment='邮箱验证情况')
    picture = Column(String(1000), nullable=False, comment='头像图片')
    active = Column(Boolean, default=False, comment='在线状态')

    session = relationship(
        'Session',
        back_populates='user',
        passive_deletes=True
    )

    user_map = relationship(
        'GroupUserMap',
        back_populates='user',
        passive_deletes=True
    )


class GroupUserMap(BaseModel):
    """
    Group Map User
    """
    user_id = Column(
        Integer,
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    group_id = Column(
        Integer,
        ForeignKey('group.id', ondelete='CASCADE'),
        nullable=False
    )

    user = relationship('User', back_populates='user_map')
    group = relationship('Group', back_populates='group_map')


class Session(BaseModel):
    """
    Session Model
    """
    platform_name = Column(String(40), nullable=False, comment='平台名称')
    token_type = Column(String(40), nullable=False, comment='token类型')
    access_token = Column(String(200), nullable=False, comment='token')
    refresh_token = Column(String(200), nullable=False, comment='刷新token')
    expires_at = Column(BigInteger, comment='过期时间')

    user_id = Column(
        Integer,
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )

    user = relationship('User', back_populates='session')
