from sqlalchemy.orm import Session
import jwt
from models import (
    AccessToken,
    RefreshToken,
    IDToken
)


def create_access_token(
        session: Session,
        token_hash: str,
        sub: str,
        iss: str,
        client_id: str,
        scope: str,
        iat: int,
        exp: int,
        status: str
):
    """
    DBにアクセストークンを登録及びトークンを作成する
    """
    token_str = jwt.encode(
        {
            "iss": iss,
            "sub": sub,
            "aud": client_id,
            "iat": iat,
            "exp": exp,
            "scope": scope,
            "jti": token_hash
        },
        key="your_secret_key",  # Replace with your actual secret key
        algorithm="HS256",
        headers={"typ": "JWT", "alg": "HS256"}
    )

    token = AccessToken(
        token_hash=token_str,
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


def update_access_token_status(session: Session, token_hash: str, status: str):
    token = get_access_token_by_hash(session, token_hash)
    if token:
        token.status = status
        session.commit()
        return token
    return None


def delete_access_token_by_hash(session: Session, token_hash: str):
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
        nonce: str = None,
        acr: str = None,
        amr: str = None,
        azp: str = None
):
    token_str = jwt.encode(
        {
            "iss": iss,
            "sub": sub,
            "aud": aud,
            "nance": nonce,
            "exp": exp,
            "iat": iat,
            "auth_time": auth_time,
            "acr": acr,
            "amr": amr,
            "azp": azp
        },
        key="your_secret_key",
        algorithm="HS256"
    )
    token = IDToken(
        sub=sub,
        iss=iss,
        aud=aud,
        iat=iat,
        exp=exp,
        auth_time=auth_time,
        nonce=nonce,
        acr=acr,
        amr=amr,
        azp=azp
    )
    session.add(token)
    session.commit()
    return token


def get_id_token_by_sub(session: Session, sub: str):
    return session.query(IDToken).filter_by(sub=sub).all()


def delete_id_token_by_hash(session: Session, id: str):
    token = session.query(IDToken).filter_by(id=id).first()
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
    token_str = jwt.encode(
        {
            "iss": iss,
            "sub": sub,
            "aud": client_id,
            "iat": iat,
            "exp": exp,
            "scope": scope,
            "jti": token_hash
        },
        key="your_secret_key",  # Replace with your actual secret key
        algorithm="HS256",
        headers={"typ": "JWT", "alg": "HS256"}
    )
    token = RefreshToken(
        token_hash=token_str,
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


def update_refresh_token_status(session: Session, token_hash: str, status: str):
    token = get_refresh_token_by_hash(session, token_hash)
    if token:
        token.status = status
        session.commit()
        return token
    return None


def delete_refresh_token_by_hash(session: Session, token_hash: str):
    token = session.query(RefreshToken).filter_by(token_hash=token_hash).first()
    if token:
        session.delete(token)
        session.commit()
        return True
    return False
