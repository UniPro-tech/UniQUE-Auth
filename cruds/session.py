from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from models.session import Session as SessionModel
from models.client import Client
from models.user import User


# 例：Clientテーブルへのレコード作成
def create_session(
    session: Session,
    session_id: str,
    auth_time: datetime,
    scope: str,
    client_obj: Client,
    user_obj: User,
    acr: str = None,
    amr: str = None,
    nonce: str = None,
    ip_address: str = None,
    user_agent: str = None,
    revoked: bool = False,
    created_at: datetime = None,
):
    new_session = SessionModel(
        session_id=session_id,
        auth_time=auth_time,
        scope=scope,
        acr=acr,
        amr=amr,
        nonce=nonce,
        ip_address=ip_address,
        user_agent=user_agent,
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
def get_session_by_id(session: Session, id: str):
    return session.query(SessionModel).filter(SessionModel.id == id).first()


# 例：session_idをキーにレコードを削除する
def delete_session_by_id(session: Session, id: str):
    get_session = get_session_by_id(session, id)
    if get_session:
        session.delete(get_session)
        session.commit()
        return True
    return False
