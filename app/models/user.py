from sqlalchemy import String
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from app.database import Base
from app.models.middle_table import (
    user_roles,
    user_flags,
    user_apps,
    app_admin_users
)
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models import (
        App,
        Client
        )


class User(Base):
    """userテーブルのモデルクラス"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    hash_password: Mapped[str] = mapped_column(String(255))

    # 多対多リレーション
    clients: Mapped[List["Client"] | None] = relationship(
        back_populates='user', cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
