from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(15), unique=True, index=True)
    name = Column(String(32))
    email = Column(String(150), unique=True, index=True)
    hashed_password = Column(String)

    created_at = Column(DateTime, default=datetime.now("UTC"))
