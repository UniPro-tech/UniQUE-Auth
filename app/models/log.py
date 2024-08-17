import time
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class Log(Base):
    __tablename__ = 'logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    app_id = Column(Integer, nullable=False, index=True)
    details = Column(String(255))
    timestamp = Column(Integer, default=int(time.time()))


class UserLog(Base):
    __tablename__ = 'user_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)
    action_at = Column(Integer, default=int(time.time()))
    description = Column(String(255))
    ipadress = Column(String(50))

    user = relationship('User', back_populates='logs')


class RoleLog(Base):
    __tablename__ = 'role_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)
    action_at = Column(Integer, default=int(time.time()))
    action_user = Column(Integer, nullable=False)
    description = Column(String(255))

    role = relationship('Role', back_populates='logs')


class FlagLog(Base):
    __tablename__ = 'flag_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)
    action_at = Column(Integer, default=int(time.time()))
    action_user = Column(Integer, nullable=False)
    description = Column(String(255))

    flag = relationship('Flag', back_populates='logs')


class AppLog(Base):
    __tablename__ = 'app_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)
    action_at = Column(Integer, default=int(time.time()))
    action_user = Column(Integer, nullable=False)
    description = Column(String(255))

    app = relationship('App', back_populates='logs')


class ClientLog(Base):
    __tablename__ = 'client_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)
    action_at = Column(Integer, default=int(time.time()))
    action_user = Column(Integer, nullable=False)
    description = Column(String(255))

    client = relationship('Client', back_populates='logs')
