from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
from models.session import Session as SessionModel
from models.client import Client, Redirect_URI


# 作成
def create_client(session: Session, client_id: int, name: str) -> Client:
    new_client = Client(
        client_id=client_id,
        name=name,
        client_type="public",
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC")),
    )
    session.add(new_client)
    session.commit()
    session.refresh(new_client)
    return new_client


# 検索（IDで）
def get_client_by_id(session: Session, client_id: str) -> Client | None:
    return session.query(Client).filter(Client.client_id == client_id).first()


# 編集
def update_client(session: Session, client_id: str, **kwargs):
    client = get_client_by_id(session, client_id)
    if not client:
        return None
    for key, value in kwargs.items():
        if hasattr(client, key):
            setattr(client, key, value)
    client.updated_at = datetime.now(ZoneInfo("UTC"))
    session.commit()
    session.refresh(client)
    return client


# 削除
def delete_client_by_id(session: Session, id: int) -> bool:
    client = get_client_by_id(session, id)
    if client:
        session.delete(client)
        session.commit()
        return True
    return False


# 作成（URIを）
def create_redirect_uri(session: Session, client_id: int, uri: str) -> Redirect_URI:
    new_uri = Redirect_URI(client_id=client_id, uri=uri)
    session.add(new_uri)
    session.commit()
    session.refresh(new_uri)
    return new_uri


# 削除（URIを）
def delete_redirect_uri(session: Session, uri: str) -> bool:
    target = session.query(Redirect_URI).filter(Redirect_URI.uri == uri).first()
    if target:
        session.delete(target)
        session.commit()
        return True
    return False
