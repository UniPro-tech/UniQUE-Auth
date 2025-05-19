from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.session import Session as SessionModel
from app.models.client import Client
from app.models.user import User


# 例：Clientテーブルへのレコード作成
def create_session(
    session: Session,
    session_id: str,
    client_obj: Client,
    user_obj: User,
    created_at: datetime = None,
):
    new_session = SessionModel(
        session_id=session_id,
        created_at=created_at or datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC")),
        client=client_obj,
        user=user_obj,
    )
    session.add(new_session)
    session.commit()          # データベースに反映
    session.refresh(new_session)  # 新しいレコードを再読み込み
    return new_session


# 例：session_idをキーに検索する
def get_session_by_session_id(session: Session, session_id: str):
    return session.query(SessionModel).filter(SessionModel.session_id == session_id).first()


# 例：session_idをキーにレコードを削除する
def delete_session_by_session_id(session: Session, session_id: str):
    get_session = get_session_by_session_id(session, session_id)
    if get_session:
        session.delete(get_session)
        session.commit()
        return True
    return False
