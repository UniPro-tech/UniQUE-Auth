from datetime import datetime
from sqlalchemy import (
    String, DateTime, Enum, Integer, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column
import enum
from database import Base


class TokenStatus(enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


# アクセストークン及び、リフレッシュトークンにはtoken_hashを保存しセキュリティを考慮する
class AccessToken(Base):
    """
    アクセストークンのモデルクラス
    token_hash: str
        アクセストークンのハッシュ値
    sub: str
        ユーザーのID
    iss: str
        レスポンスを返した Issuer の Issuer Identifier。httpsスキーマで始まるURL
    client_id: str
        クライアントのID
    scope: str
        アクセストークンのスコープ
    iat: datetime
        発行日時
    exp: datetime
        有効期限
    status: TokenStatus
        トークンの状態（active, revoked, expired）
    """
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
    """
    IDトークンのモデルクラス
    id: int
        ID（管理用）
    sub: str
        ユーザーのID
    iss: str
        レスポンスを返した Issuer の Issuer Identifier。httpsスキーマで始まるURL
    aud: str
        client_id
    iat: datetime
        発行日時
    exp: datetime
        有効期限
    auth_time: datetime
        認証時刻
    nonce: str
        認証リクエストに含まれるnonce
    acr: str
        認証要求に含まれる認証方式
    amr: str
        認証要求に含まれる認証方法
    azp: str
        認可されたクライアントのID
    """
    __tablename__ = "id_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sub: Mapped[str] = mapped_column(String(255), nullable=False)
    iss: Mapped[str] = mapped_column(String(255), nullable=False)
    aud: Mapped[str] = mapped_column(String(255), nullable=False)
    iat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    auth_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    nonce: Mapped[str] = mapped_column(String(255), nullable=True)
    acr: Mapped[str] = mapped_column(String(255), nullable=True)
    amr: Mapped[str] = mapped_column(String(255), nullable=True)
    azp: Mapped[str] = mapped_column(String(255), nullable=True)


class RefreshToken(Base):
    """
    リフレッシュトークンのモデルクラス
    id: int
        リフレッシュトークンのID
    token_hash: str
        リフレッシュトークンのハッシュ値
    sub: str
        ユーザーのID
    iss: str
        レスポンスを返した Issuer の Issuer Identifier。httpsスキーマで始まるURL
    client_id: str
        クライアントのID
    scope: str
        アクセストークンのスコープ
    iat: datetime
        発行日時
    exp: datetime
        有効期限
    status: TokenStatus
        トークンの状態（active, revoked, expired）
    rotated_from_id: int
        リフレッシュトークンのローテーション元のID(追跡用)
    """
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
