from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from typing import TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
    from app.models import (
        User,
        App,
        Token
        )


class Client(Base):
    """clientテーブルのモデルクラス"""

    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    app_id: Mapped[int] = mapped_column(ForeignKey('apps.id'), nullable=True)

    user: Mapped['User'] = relationship(back_populates='clients')
    app: Mapped['App'] = relationship(back_populates='clients')

    # 1対1のリレーションシップ：Clientは1つのトークンしか持てない
    acsess_token: Mapped['Token'] = relationship(
            back_populates='client', cascade='all, delete-orphan'
        )
    refresh_token: Mapped['Token'] = relationship(
            back_populates='client', cascade='all, delete-orphan'
        )

    def __repr__(self):
        return f"<Client(id={self.id}, user_id={self.user_id}, app_id={self.app_id})>"
