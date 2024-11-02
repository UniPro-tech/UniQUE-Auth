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
        Role,
        Flag,
        App,
        Log,
        Client
        )


class User(Base):
    """userテーブルのモデルクラス"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    hash_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(30))
    email_verified: Mapped[bool] = mapped_column(default=False)
    is_enable: Mapped[bool] = mapped_column(default=True)
    # 多対多リレーション
    roles: Mapped[List["Role"] | None] = relationship(
        secondary=user_roles, back_populates="users"
    )
    flags: Mapped[List["Flag"] | None] = relationship(
        secondary=user_flags, back_populates="users"
    )
    apps: Mapped[List["App"] | None] = relationship(
        secondary=user_apps, back_populates="users"
    )
    admin_apps: Mapped[List["App"]] = relationship(
        secondary=app_admin_users, back_populates="admin_users"
    )
    clients: Mapped[List["Client"] | None] = relationship(
        back_populates='user', cascade="all, delete-orphan"
    )
    # 多対一リレーション
    logs: Mapped[List["Log"] | None] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
