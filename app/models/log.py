import time
from sqlalchemy import String, ForeignKey
from app.database import Base
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import (
        User,
        App
        )


class Log(Base):
    __tablename__ = 'logs'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    action_at: Mapped[int] = mapped_column(default=time.time())
    action_entity: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255))

    # UserおよびAppテーブルへの外部キーを設定
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    app_id: Mapped[int] = mapped_column(ForeignKey("apps.id"))

    # UserおよびAppテーブルとのリレーションシップを設定
    user: Mapped["User"] = relationship(back_populates="logs")
    app: Mapped["App"] = relationship(back_populates="logs")

    def __repr__(self):
        return f"<Log id={self.id}, action_type={self.action_type}, action_entity={self.action_entity}>"
