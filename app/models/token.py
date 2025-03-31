from sqlalchemy import ForeignKey
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

    id: Mapped[str] = mapped_column(primary_key=True, index=True, unique=True)
    auth_time: Mapped[int] = mapped_column(index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))

    # Tokenは1つのクライアントにのみ紐付けられる
    client: Mapped["Client"] = relationship(back_populates="token")

    def __repr__(self):
        return f"<Token id={self.id}, client_id={self.client.id}>"
