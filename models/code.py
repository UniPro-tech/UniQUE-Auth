from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from zoneinfo import ZoneInfo
from database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import Session, Client


class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    code: Mapped[str] = mapped_column(String(255), primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    redirect_uri: Mapped[str] = mapped_column(String(255))
    scope: Mapped[str] = mapped_column(String(255))
    nonce: Mapped[str] = mapped_column(String(255), nullable=True)
    auth_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("UTC")))
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    session: Mapped["Session"] = relationship("Session", back_populates="authorization_codes")
    client: Mapped[Client] = relationship("Client", back_populates="authorization_codes")
