from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from unique_api.app.db import Base
from unique_api.app.model.util import generate_ulid

if TYPE_CHECKING:
    from unique_api.app.model.auth import Auths
    from unique_api.app.model.intermediate import UserApp, UserRole


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("custom_id", "custom_id", unique=True),
        Index("email", "email", unique=True),
        Index("idx_users_custom_id", "custom_id"),
    )

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    name: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    password_hash: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    external_email: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    period: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_system: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
    custom_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    email: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    email_verified: Mapped[Optional[bool]] = mapped_column(
        TINYINT(1), server_default=text("'0'")
    )
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_enable: Mapped[Optional[int]] = mapped_column(
        TINYINT(1), server_default=text("'1'")
    )

    auths: Mapped[List["Auths"]] = relationship("Auths", back_populates="auth_user")
    discords: Mapped[List["Discords"]] = relationship("Discords", back_populates="user")
    sessions: Mapped[List["Sessions"]] = relationship("Sessions", back_populates="user")
    user_app: Mapped[List["UserApp"]] = relationship("UserApp", back_populates="user")
    user_role: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="user"
    )


class Discords(Base):
    __tablename__ = "discords"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="discords_ibfk_1"),
        Index("discord_id", "discord_id", unique=True),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discord_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))

    user: Mapped["Users"] = relationship("Users", back_populates="discords")


class Sessions(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="sessions_ibfk_1"),
        Index("user_id", "user_id"),
    )

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    ip_address: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    user_agent: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    user: Mapped["Users"] = relationship("Users", back_populates="sessions")
