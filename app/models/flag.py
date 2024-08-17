from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_flags


class Flag(Base):
    __tablename__ = "flags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    image_url = Column(String, index=True)

    # 多対多リレーション
    users = relationship(
        'User', secondary=user_flags, back_populates='flags'
        )

    # 多対一リレーション
    logs = relationship('Log', back_populates='app')
