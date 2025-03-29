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
        Client
        )


class App(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    scope: Mapped[str] = mapped_column(String(255), index=True)
    redirect_uri: Mapped[str] = mapped_column(String(255), index=True)

    # 多対一リレーション
    clients: Mapped[List["Client"] | None] = relationship(
        back_populates='app', cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<App(id={self.id}, name={self.name})>"
