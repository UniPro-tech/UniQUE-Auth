from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.database import Base
from app.models.middle_table import user_apps, app_admin_users
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models import (
        User,
        Client,
        Log
        )


class App(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    image_url: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(String(500), default="")
    verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    # 多対多リレーション
    users: Mapped[List["User"]] = relationship(
        secondary=user_apps, back_populates='apps'
    )
    admin_users: Mapped[List["User"]] = relationship(
        secondary=app_admin_users, back_populates='admin_apps'
    )

    # 多対一リレーション
    logs: Mapped[List["Log"] | None] = relationship(back_populates="app")
    clients: Mapped[List["Client"] | None] = relationship(
        back_populates='app', cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<App(id={self.id}, name={self.name})>"
