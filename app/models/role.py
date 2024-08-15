from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_roles


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    permission_bit = Column(Integer, default=0)
    sort = Column(Integer, default=100)

    # 多対多リレーション
    users = relationship(
        'User', secondary=user_roles, back_populates='roles'
        )

    # 多対一リレーション
    logs = relationship('Log', back_populates='app')
