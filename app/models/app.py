from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_apps, app_admin_users


class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image_url = Column(String)
    description = Column(String, index=True)
    verified = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)

    # 多対多リレーション
    users = relationship(
        'User', secondary=user_apps, back_populates='apps'
        )
    admin_users = relationship(
        'User', secondary=app_admin_users, back_populates='admin_apps'
        )

    # 多対一リレーション
    logs = relationship('AppLog', back_populates='app')
    clients = relationship('Client', back_populates='app')
