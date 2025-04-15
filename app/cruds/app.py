from sqlalchemy.orm import Session
from app.models.app import App, Redirect_URI


# 作成
def create_app(session: Session, name: str, scope: str, **kwargs) -> App:
    new_app = App(name=name, scope=scope, **kwargs)
    session.add(new_app)
    session.commit()
    session.refresh(new_app)
    return new_app


# 検索（名前で）
def get_app_by_name(session: Session, name: str) -> App | None:
    return session.query(App).filter(App.name == name).first()


# 削除（名前で）
def delete_app_by_name(session: Session, name: str) -> bool:
    app = get_app_by_name(session, name)
    if app:
        session.delete(app)
        session.commit()
        return True
    return False


# 作成
def create_redirect_uri(session: Session, app_id: int, uri: str) -> Redirect_URI:
    new_uri = Redirect_URI(app_id=app_id, uri=uri)
    session.add(new_uri)
    session.commit()
    session.refresh(new_uri)
    return new_uri


# 検索（app_idごと）
def get_redirect_uris_by_app_id(session: Session, app_id: int) -> list[Redirect_URI]:
    return session.query(Redirect_URI).filter(Redirect_URI.app_id == app_id).all()


# 削除（URIで）
def delete_redirect_uri(session: Session, uri: str) -> bool:
    target = session.query(Redirect_URI).filter(Redirect_URI.uri == uri).first()
    if target:
        session.delete(target)
        session.commit()
        return True
    return False
