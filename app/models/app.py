from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.database import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models import Client


class App(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    scope: Mapped[str] = mapped_column(String(255), index=True)
    redirect_uris: Mapped[List["Redirect_URI"]] = relationship(
        back_populates="app"
    )

    # 多対一リレーション
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
