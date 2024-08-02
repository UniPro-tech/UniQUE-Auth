from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    tokenid = Column(String, index=True)
    userid = Column(String, index=True)
    appid = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
