from datetime import datetime
from sqlalchemy import (
    String, DateTime, Enum, Integer, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.database import Base


class TokenStatus(enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


# アクセストークン及び、リフレッシュトークンにはtoken_hashを保存しセキュリティを考慮する
class AccessToken(Base):
    __tablename__ = "access_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    sub: Mapped[str] = mapped_column(String(255), nullable=False)
    iss: Mapped[str] = mapped_column(String(255), nullable=False)
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(512), nullable=True)
    iat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[TokenStatus] = mapped_column(Enum(TokenStatus), default=TokenStatus.ACTIVE, nullable=False)


class IDToken(Base):
    __tablename__ = "id_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sub: Mapped[str] = mapped_column(String(255), nullable=False)
    iss: Mapped[str] = mapped_column(String(255), nullable=False)
    aud: Mapped[str] = mapped_column(String(255), nullable=False)
    iat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    auth_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    nonce: Mapped[str] = mapped_column(String(255), nullable=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    sub: Mapped[str] = mapped_column(String(255), nullable=False)
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)
    iss: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(512), nullable=True)
    iat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[TokenStatus] = mapped_column(Enum(TokenStatus), default=TokenStatus.ACTIVE, nullable=False)
    rotated_from_id: Mapped[int] = mapped_column(Integer, ForeignKey("refresh_tokens.id"), nullable=True)
