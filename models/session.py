from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from typing import TYPE_CHECKING
from datetime import datetime
from zoneinfo import ZoneInfo
from database import Base

if TYPE_CHECKING:
    from models import (
        User,
        Client
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # セッションID
    session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)  # セッションID
    auth_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 認証日時
    scope: Mapped[str] = mapped_column(String(255), nullable=False)  # スコープ
    acr: Mapped[str] = mapped_column(String(255), nullable=False)  # 認証レベル
    amr: Mapped[str] = mapped_column(String(255), nullable=False)  # 認証方法
    nonce: Mapped[str] = mapped_column(String(255), nullable=False)  # nonce

    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPアドレス
    user_agent: Mapped[str] = mapped_column(String(255), nullable=False)  # ユーザーエージェント

    revoked: Mapped[bool] = mapped_column(default=False, nullable=False)  # セッションが取り消されたかどうか

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("UTC")))  # 作成日時
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(ZoneInfo("UTC")), onupdate=datetime.now(ZoneInfo("UTC"))
    )  # 更新日時

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))  # 外部キーとしてClientテーブルのIDを参照
    client: Mapped["Client"] = relationship("Client", back_populates="sessions")  # Clientとのリレーション

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # 外部キーとしてUserテーブルのIDを参照
    user: Mapped["User"] = relationship("User", back_populates="sessions")  # Userとのリレーション

    def __repr__(self):
        return f"<Session(id={self.id}, session_id={self.session_id}, client_id={self.client_id}, user_id={self.user_id})>"
