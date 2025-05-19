from sqlalchemy.orm import Session
from app.models import (
    AccessToken,
    RefreshToken,
    IDToken
)


def create_access_token(
        session: Session,
        token_hash: str,
        sub: str, iss: str,
        client_id: str,
        scope: str,
        iat: int,
        exp: int,
        status: str
):
    token = AccessToken(
        token_hash=token_hash,
        sub=sub,
        iss=iss,
        client_id=client_id,
        scope=scope,
        iat=iat,
        exp=exp,
        status=status
    )
    session.add(token)
    session.commit()
    return token


def get_access_token_by_hash(session: Session, token_hash: str):
    return session.query(AccessToken).filter_by(token_hash=token_hash).first()


def delete_access_token(session: Session, token_hash: str):
    token = session.query(AccessToken).filter_by(token_hash=token_hash).first()
    if token:
        session.delete(token)
        session.commit()
        return True
    return False


def create_id_token(
        session: Session,
        sub: str,
        iss: str,
        aud: str,
        iat: int,
        exp: int,
        auth_time: int = None,
        nonce: str = None
):
    token = IDToken(
        sub=sub,
        iss=iss,
        aud=aud,
        iat=iat,
        exp=exp,
        auth_time=auth_time,
        nonce=nonce
    )
    session.add(token)
    session.commit()
    return token


def get_id_token_by_sub(session: Session, sub: str):
    return session.query(IDToken).filter_by(sub=sub).all()


def delete_id_token(session: Session, token_id: str):
    token = session.query(IDToken).filter_by(id=token_id).first()
    if token:
        session.delete(token)
        session.commit()
        return True
    return False


def create_refresh_token(
    session: Session,
    token_hash: str,
    sub: str,
    client_id: str,
    iss: str,
    scope: str,
    iat: int,
    exp: int,
    status: str,
    rotated_from_id: str = None
):
    token = RefreshToken(
        token_hash=token_hash,
        sub=sub,
        client_id=client_id,
        iss=iss,
        scope=scope,
        iat=iat,
        exp=exp,
        status=status,
        rotated_from_id=rotated_from_id
    )
    session.add(token)
    session.commit()
    return token


def get_refresh_token_by_hash(session: Session, token_hash: str):
    return session.query(RefreshToken).filter_by(token_hash=token_hash).first()


def delete_refresh_token(session: Session, token_hash: str):
    token = session.query(RefreshToken).filter_by(token_hash=token_hash).first()
    if token:
        session.delete(token)
        session.commit()
        return True
    return False
