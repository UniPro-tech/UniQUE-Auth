from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_apps


class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, index=True)
    created_at = Column(Integer)
    updated_at = Column(Integer)
    deleted_at = Column(Integer)
    is_locked = Column(Boolean, default=False)

    # 多対多リレーション
    users = relationship('User', secondary=user_apps, back_populates='apps')
