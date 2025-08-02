from typing import List, Optional, TYPE_CHECKING
import base64
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
    __table_args__ = (Index("client_id", "client_id", unique=True),)

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    client_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    aud: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
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

    def verify_client_secret(self, authorization: str | None) -> bool:
        """
        クライアントシークレットを検証するメソッド。
        authorization ヘッダーが "Basic {base64エンコードされたクライアントID:クライアントシークレット}" 形式であることを確認します。
        """
        if authorization is None:
            return False

        try:
            # "Basic " プレフィックスを除去
            auth_value = authorization.split(" ")[1]
            decoded = base64.b64decode(auth_value).decode("utf-8")
            client_id, client_secret = decoded.split(":", 1)

            # クライアントIDとクライアントシークレットを比較
            return (
                client_id == self.client_id and client_secret == self.client_secret
            )
        except (ValueError, IndexError):
            return False


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
