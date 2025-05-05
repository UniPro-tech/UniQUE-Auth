from sqlalchemy import String
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from app.database import Base
from typing import TYPE_CHECKING, List
from passlib.context import CryptContext
import hashlib

if TYPE_CHECKING:
    from app.models import (
        Client
    )


class User(Base):
    """userテーブルのモデルクラス"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    hash_password: Mapped[str] = mapped_column(String(255))

    # 多対多リレーション
    clients: Mapped[List["Client"] | None] = relationship(
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
