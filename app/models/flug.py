from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base


class Flag(Base):
    __tablename__ = "flugs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, index=True)
    users = Column(String, index=True)
    created_at = Column(Integer)
    updated_at = Column(Integer)
    deleted_at = Column(Integer)
    is_deleted = Column(Boolean, default=False)
