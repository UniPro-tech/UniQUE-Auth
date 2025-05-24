from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from models import AuthorizationCode


def create_code(
    session: Session,
    code: str,
    session_id: int,
    client_id: str,
    redirect_uri: str,
    scope: str,
    auth_time: datetime = None,
    nonce: str = None,
    created_at: datetime = None,
    expires_at: datetime = None
):
    new_code = AuthorizationCode(
        code=code,
        session_id=session_id,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        nonce=nonce,
        auth_time=auth_time,
        created_at=created_at or datetime.now(ZoneInfo("UTC")),
        expires_at=expires_at
    )
    session.add(new_code)
    session.commit()
    session.refresh(new_code)
    return new_code


def get_code_by_code(session: Session, code: str):
    return session.query(AuthorizationCode).filter(AuthorizationCode.code == code).first()


def delete_code_by_code(session: Session, code: str):
    code_instance = get_code_by_code(session, code)
    if code_instance:
        session.delete(code_instance)
        session.commit()
        return True
    return False
