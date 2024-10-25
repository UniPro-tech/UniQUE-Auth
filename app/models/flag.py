from sqlalchemy import String
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from app.database import Base
from app.models.middle_table import user_flags, flag_admin_users, flag_roles
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import (
        User,
        Role,
        Log
        )


class Flag(Base):
    __tablename__ = "flags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(30), index=True)
    description: Mapped[str] = mapped_column(String(500))
    image_url: Mapped[str] = mapped_column(String(255))
    is_enabled: Mapped[bool] = mapped_column(nullable=False)
    can_assign: Mapped[bool] = mapped_column(nullable=False)

    # 多対多リレーション
    users: Mapped[list["User"]] = relationship(
        secondary=user_flags, back_populates='flags'
    )
    admin_users: Mapped[list["User"]] = relationship(
        secondary=flag_admin_users, back_populates='admin_flags'
    )
    roles: Mapped[list["Role"]] = relationship(
        secondary=flag_roles, back_populates='flags'
    )
    # 多対一リレーション
    logs: Mapped[list["Log"]] = relationship(back_populates='flag')

    def __repr__(self):
        return f"<Flag(id={self.id}, name={self.name})>"
