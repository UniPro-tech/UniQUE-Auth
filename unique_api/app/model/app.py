from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    ForeignKeyConstraint,
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
    from unique_api.app.model.intermediate import UserApp
    from unique_api.app.model.auth import Auths


class Apps(Base):
    __tablename__ = "apps"

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    client_secret: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    name: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    auths: Mapped[List["Auths"]] = relationship("Auths", back_populates="app")
    redirect_uris: Mapped[List["RedirectUris"]] = relationship(
        "RedirectUris", back_populates="app"
    )
    user_app: Mapped[List["UserApp"]] = relationship("UserApp", back_populates="app")


class RedirectUris(Base):
    __tablename__ = "redirect_uris"
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="redirect_uris_ibfk_1"),
        Index("app_id", "app_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    uri: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    app: Mapped["Apps"] = relationship("Apps", back_populates="redirect_uris")
