from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from .middle_table import user_flags, flag_admin_users, flag_roles


class Flag(Base):
    __tablename__ = "flags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    display_name = Column(String, index=True)
    description = Column(String, index=True)
    image_url = Column(String)
    is_enabled = Column(Boolean, default=True)
    can_assign = Column(Boolean, default=True)

    # 多対多リレーション
    users = relationship(
        'User', secondary=user_flags, back_populates='flags'
        )
    admin_users = relationship(
        'User', secondary=flag_admin_users, back_populates='admin_apps'
        )
    roles = relationship(
        'Role', secondary=flag_roles, back_populates='flags'
    )

    # 多対一リレーション
    logs = relationship('Log', back_populates='app')
