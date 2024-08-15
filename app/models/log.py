import time
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Log(Base):
    __tablename__ = 'logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String(50), nullable=False)
    user_id = Column(
        Integer, ForeignKey('users.id'), nullable=True, index=True
        )
    app_id = Column(
        Integer, ForeignKey('apps.id'), nullable=True, index=True
        )
    flag_id = Column(
        Integer, ForeignKey('flags.id'), nullable=True, index=True
        )
    details = Column(String(255))
    timestamp = Column(Integer, default=int(time.time()))

    user = relationship('User', back_populates='logs')
    app = relationship('App', back_populates='logs')
    flag = relationship('Flag', back_populates='logs')
