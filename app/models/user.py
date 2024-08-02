from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_roles, user_flags, user_apps


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    name = Column(String, primary_key=True, index=True)
    email = Column(String, index=True)
    hash_password = Column(String)
    display_name = Column(String, index=True)

    # 多対多リレーション
    roles = relationship(
        'Role', secondary=user_roles, back_populates='users'
        )
    flags = relationship(
        'Flag', secondary=user_flags, back_populates='users'
        )
    apps = relationship(
        'App', secondary=user_apps, back_populates='users'
        )
    # 多対一リレーション
    logs = relationship('UserLog', back_populates='user')

    email_verified = Column(Boolean, default=False)
    is_enable = Column(Boolean, default=False)
