from sqlalchemy import String
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from app.database import Base
from app.models.middle_table import user_flags
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import (
        User
        )


class Flag(Base):
    __tablename__ = "flags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True, unique=True)
    display_name: Mapped[str] = mapped_column(String(30), index=True)
    description: Mapped[str] = mapped_column(String(500), default="")
    image_url: Mapped[str] = mapped_column(String(255), default="")
    is_enabled: Mapped[bool] = mapped_column(nullable=False)
    can_assign: Mapped[bool] = mapped_column(nullable=False)

    # 多対多リレーション
    users: Mapped[list["User"]] = relationship(
        secondary=user_flags, back_populates='flags'
    )

    def __repr__(self):
        return f"<Flag(id={self.id}, name={self.name})>"
