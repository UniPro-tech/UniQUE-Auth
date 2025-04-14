from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from datetime import datetime
from zoneinfo import ZoneInfo
from app.database import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models import Client


class App(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    scope: Mapped[str] = mapped_column(String(255), index=True)
    
    client_type: Mapped[str] = mapped_column(String(30), default="confidential")  # confidential or public
    grant_types: Mapped[str] = mapped_column(String(255), default="authorization_code")
    response_types: Mapped[str] = mapped_column(String(255), default="code")
    token_endpoint_auth_method: Mapped[str] = mapped_column(String(50), default="client_secret_basic")

    logo_uri: Mapped[str] = mapped_column(String(255), nullable=True)
    client_uri: Mapped[str] = mapped_column(String(255), nullable=True)
    tos_uri: Mapped[str] = mapped_column(String(255), nullable=True)
    policy_uri: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("UTC")))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(ZoneInfo("UTC")), onupdate=datetime.now(ZoneInfo("UTC"))
    )

    redirect_uris: Mapped[List["Redirect_URI"]] = relationship(
        back_populates="app"
    )

    clients: Mapped[List["Client"]] = relationship(
        back_populates='app', cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<App(id={self.id}, name={self.name}, scope={self.scope})>"


class Redirect_URI(Base):
    __tablename__ = "redirect_uris"

    id: Mapped[int] = mapped_column(primary_key=True)
    uri: Mapped[str] = mapped_column(String(255))
    app_id: Mapped[int] = mapped_column(ForeignKey("apps.id"))
    app: Mapped["App"] = relationship(back_populates="redirect_uris")

    def __repr__(self):
        return f"<Redirect_URI(id={self.id}, uri={self.uri})>"
