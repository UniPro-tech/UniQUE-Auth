from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    is_enable = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    app_id = Column(Integer, ForeignKey('apps.id'))

    user = relationship('User', back_populates='clients')
    app = relationship('App', back_populates='clients')
