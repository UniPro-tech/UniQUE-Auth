from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer,
    Index,
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
    from unique_api.app.model.intermediate import UserRole


class Roles(Base):
    __tablename__ = "roles"
    __table_args__ = (
        Index("custom_id", "custom_id", unique=True),
        {"comment": "ロール情報"},
    )

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    name: Mapped[Optional[str]] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), nullable=True
    )
    permissions: Mapped[int] = mapped_column(Integer, server_default=text("'0'"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    is_system: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
    custom_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    user_role: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="role"
    )
