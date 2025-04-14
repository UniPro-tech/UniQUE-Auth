from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from typing import TYPE_CHECKING
from app.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from app.models import (
        User,
        App
        )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # クライアントID
    client_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # ユニークなクライアントID
    client_secret: Mapped[str] = mapped_column(String(255), nullable=False)  # クライアントシークレット（ハッシュ化推奨）
    client_type: Mapped[str] = mapped_column(String(30), default="confidential")  # "confidential" or "public"
    grant_types: Mapped[str] = mapped_column(String(255), default="authorization_code")  # 使用するgrantタイプ（スペース区切り）
    response_types: Mapped[str] = mapped_column(String(255), default="code")  # 使用するレスポンスタイプ
    token_endpoint_auth_method: Mapped[str] = mapped_column(String(50), default="client_secret_basic")  # 認証方式

    logo_uri: Mapped[str] = mapped_column(String(255), nullable=True)  # ロゴURI
    client_uri: Mapped[str] = mapped_column(String(255), nullable=True)  # クライアント情報ページURI
    tos_uri: Mapped[str] = mapped_column(String(255), nullable=True)  # 利用規約URI
    policy_uri: Mapped[str] = mapped_column(String(255), nullable=True)  # プライバシーポリシーURI

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(ZoneInfo("UTC")))  # 作成日時
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(ZoneInfo("UTC")), onupdate=datetime.now(ZoneInfo("UTC"))
    )  # 更新日時

    app_id: Mapped[int] = mapped_column(ForeignKey("apps.id"))  # 外部キーとしてAppテーブルのIDを参照
    app: Mapped["App"] = relationship("App", back_populates="clients")  # Appとのリレーション

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # 外部キーとしてUserテーブルのIDを参照
    user: Mapped["User"] = relationship("User", back_populates="clients")  # Userとのリレーション

    def __repr__(self):
        return f"<Client(id={self.id}, client_id={self.client_id}, client_type={self.client_type})>"
