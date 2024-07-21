from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    name = Column(String, primary_key=True, index=True)
    email = Column(String, index=True)
    hash_password = Column(String)
    display_name = Column(String, index=True)

    # 後ほどリレーション
    roles = Column(String, index=True)
    flugs = Column(String, index=True)
    apps = Column(String, index=True)

    created_at = Column(Integer)
    updated_at = Column(Integer)
    deleted_at = Column(Integer)
    is_bot = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
