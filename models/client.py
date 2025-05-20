from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING, List

from database import Base


if TYPE_CHECKING:
    from models import Session


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    client_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    client_type: Mapped[str] = mapped_column(String(255), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("UTC")))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(ZoneInfo("UTC")), onupdate=datetime.now(ZoneInfo("UTC"))
    )

    redirect_uris: Mapped[List["Redirect_URI"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )

    sessions: Mapped[List["Session"]] = relationship(
        back_populates='client', cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Client(id={self.id}, client_id={self.client_id}, client_type={self.client_type})>"


class Redirect_URI(Base):
    __tablename__ = "redirect_uris"

    id: Mapped[int] = mapped_column(primary_key=True)
    uri: Mapped[str] = mapped_column(String(255))
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    client: Mapped["Client"] = relationship(back_populates="redirect_uris")

    def __repr__(self):
        return f"<Redirect_URI(id={self.id}, uri={self.uri})>"
