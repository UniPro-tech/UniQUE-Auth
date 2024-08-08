from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_apps


class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String)
    name = Column(String, index=True)
    image_url = Column(String)
    description = Column(String, index=True)
    enabled = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)

    # 多対多リレーション
    users = relationship(
        'User', secondary=user_apps, back_populates='apps'
        )

    # 多対一リレーション
    logs = relationship('AppLog', back_populates='app')
    clients = relationship('Client', back_populates='app')
