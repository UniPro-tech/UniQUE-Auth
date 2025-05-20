from sqlalchemy import String
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from typing import TYPE_CHECKING, List
import hashlib

from database import Base
if TYPE_CHECKING:
    from models import Session


class User(Base):
    """userテーブルのモデルクラス"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    hash_password: Mapped[str] = mapped_column(String(255))

    # 多対多リレーション
    sessions: Mapped[List["Session"] | None] = relationship(
        back_populates='user', cascade="all, delete-orphan"
    )

    def verify_password(self, password: str) -> bool:
        """パスワードを検証するメソッド"""
        # ここでは、パスワードのハッシュ化と比較を行う
        # 実際の実装では、適切なハッシュ化ライブラリを使用してください
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == self.hash_password

        # 例: return bcrypt.checkpw(password.encode('utf-8'), self.hash_password.encode('utf-8'))

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
