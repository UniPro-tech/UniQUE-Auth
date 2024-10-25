from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from ..database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models import Client


class Token(Base):
    """Tokenテーブルのモデルクラス"""

    __tablename__ = "token"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    acsess_token: Mapped[str] = mapped_column(String(100), index=True)
    refresh_token: Mapped[str] = mapped_column(String(100), index=True)
    is_enabled: Mapped[bool] = mapped_column(default=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))

    # Tokenは1つのクライアントにのみ紐付けられる
    client: Mapped["Client"] = relationship(back_populates="token")

    def __repr__(self):
        return f"<Token id={self.id}, client_id={self.client.id}>"
