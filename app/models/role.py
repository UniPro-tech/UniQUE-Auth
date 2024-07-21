from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    display_name = Column(String, index=True)
    description = Column(String, index=True)
    permission_bits = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
    read_only = Column(Boolean, default=False)
    can_assign = Column(Boolean, default=False)

