from sqlalchemy import Table, ForeignKey, Column, Integer
from ..database import Base


# UserとAppの多対多リレーション
user_apps = Table(
    'user_apps',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('app_id', Integer, ForeignKey('apps.id'), primary_key=True)
)
