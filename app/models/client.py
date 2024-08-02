from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_clients


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    is_enabled = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)

    # 多対多リレーション
    users = relationship(
        'User', secondary=user_clients, back_populates='clients'
        )
