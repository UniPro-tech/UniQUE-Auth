from sqlalchemy import String
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from ..database import Base
from .middle_table import user_roles
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import (
        User,
        Log
        )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    display_name: Mapped[str] = mapped_column(String(30), index=True)
    description: Mapped[str] = mapped_column(String(500))
    permission_bit: Mapped[int] = mapped_column(nullable=False)
    is_enabled: Mapped[bool] = mapped_column(nullable=False)
    is_deactivated: Mapped[bool] = mapped_column(nullable=False)
    sort: Mapped[int] = mapped_column(nullable=False)

    # 多対多リレーション
    users: Mapped[list["User"]] = relationship(
        secondary=user_roles, back_populates='roles'
    )
    # 多対一リレーション
    logs: Mapped[list["Log"]] = relationship(back_populates='role')

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, permission_bit={self.permission_bit})>"
