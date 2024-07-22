from sqlalchemy import Table, ForeignKey, Column, Integer
from ..database import Base

# UserとRoleの多対多リレーション
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# UserとFlagの多対多リレーション
user_flags = Table(
    'user_flags',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('flag_id', Integer, ForeignKey('flags.id'), primary_key=True)
)

# UserとAppの多対多リレーション
user_apps = Table(
    'user_apps',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('app_id', Integer, ForeignKey('apps.id'), primary_key=True)
)
