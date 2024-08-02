from sqlalchemy import Table, ForeignKey, Column, Integer
from ..database import Base

# UserとRoleの多対多リレーション
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

# UserとFlagの多対多リレーション
user_flags = Table(
    'user_flags',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('flag_id', Integer, ForeignKey('flugs.id'))
)

# UserとAppの多対多リレーション
user_apps = Table(
    'user_apps',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('app_id', Integer, ForeignKey('apps.id'))
)

# userとclientの多対多リレーション
user_clients = Table(
    'user_clients',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('client_id', Integer, ForeignKey('clients'))
)

# appとclientの多対多リレーション
app_clients = Table(
    'app_clients',
    Base.metadata,
    Column('app_id', Integer, ForeignKey('apps.id')),
    Column('client_id', Integer, ForeignKey('clients'))
)
