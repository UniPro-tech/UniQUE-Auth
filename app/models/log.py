import time
from sqlalchemy import Column, Integer, String
from ..database import Base


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String(50), nullable=False, index=True)
    action_at = Column(Integer, default=int(time.time()))
    action_entity = Column(Integer, nullable=False, index=True)
    description = Column(String(255))

    def __repr__(self):
        return f"<Log id={self.id}, action_type={self.action_type}, action_entity={self.action_entity}>"
