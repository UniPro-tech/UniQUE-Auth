from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from unique_api.app.db import Base

if TYPE_CHECKING:
    from unique_api.app.model.app import Apps
    from unique_api.app.model.user import Users
    from unique_api.app.model.role import Roles


class UserApp(Base):
    __tablename__ = "user_app"
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="user_app_ibfk_1"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_app_ibfk_2"),
        Index("app_id", "app_id"),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    user_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))

    app: Mapped[Optional["Apps"]] = relationship("Apps", back_populates="user_app")
    user: Mapped[Optional["Users"]] = relationship("Users", back_populates="user_app")


class UserRole(Base):
    __tablename__ = "user_role"
    __table_args__ = (
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="user_role_ibfk_2"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_role_ibfk_1"),
        Index("role_id", "role_id"),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    role_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))

    role: Mapped["Roles"] = relationship("Roles", back_populates="user_role")
    user: Mapped["Users"] = relationship("Users", back_populates="user_role")
