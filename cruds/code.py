from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from models import AuthorizationCode


def create_token(
    payload: str,
    secret: str,
    header: dict = {"typ": "JWT", "alg": "HS256"},
    algorithm: str = "HS256"
):
    """
    ヘッダーとペイロードはbase64でエンコードする
    """
    import jwt

    token = jwt.encode(
        payload=payload,
        key=secret,
        algorithm=algorithm,
        headers=header,
    )
    return token


def create_access_token(
        iss: str,
        sub: str,
        aud: str,
        exp: int,
        iat: int,
        jti: str = None,
        scope: str = None,
) -> str:
    return create_token(
        payload={
            "iss": iss,
            "sub": sub,
            "aud": aud,
            "exp": exp,
            "iat": iat,
            "jti": jti,
            "scope": scope,
        },
        secret="your_secret_key",  # Replace with your actual secret key
    )


def create_refresh_token(
        iss: str,
        sub: str,
        aud: str,
        iat: int,
        exp: int,
) -> str:
    return create_token(
        payload={
            "iss": iss,
            "sub": sub,
            "aud": aud,
            "iat": iat,
            "exp": exp
        },
        secret="your_secret_key",  # Replace with your actual secret key
    )


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
