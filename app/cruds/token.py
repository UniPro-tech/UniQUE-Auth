import os
from sqlalchemy.orm import Session
from uuid_extensions import uuid7str
import jwt
from .. import schemas
from ..models import Token
from dotenv import load_dotenv


# .envファイルの内容を読み込見込む
load_dotenv(dotenv_path='../../.env')


__SQLALCHEMY_DATABASE_URI = os.environ['SECRET_KEY']


def create_access_token(
        token: schemas.AccessToken
        ) -> str:
    uuid = uuid7str()

    access_token = jwt.encode(
        payload={
            'iss': token.iss,
            'sub': token.sub,
            'exp': token.exp,
            'iat': token.iat,
            'scope': token.scope,
            'for': token.for_,
            'jti': uuid
        },
        key=__SQLALCHEMY_DATABASE_URI,
        algorithm=token.alg,
        headers={'alg': token.alg, 'typ': token.typ}
    )

    return access_token, uuid


def create_refresh_token(
        token: schemas.RefreshToken
        ) -> str:
    uuid = uuid7str()
    # TODO:トークンをDBに保存する処理を追加する
    refresh_token = jwt.encode(
        payload={
            'iss': token.iss,
            'sub': token.sub,
            'exp': token.exp,
            'iat': token.iat,
            'jti': uuid,
            'for': token.for_
        },
        key=__SQLALCHEMY_DATABASE_URI,
        algorithm=token.alg,
        headers={'alg': token.alg, 'typ': token.typ}
    )
    return refresh_token, uuid


async def add_db_token(
        db: Session, jti: str, user_id: int,
        app_id: int, is_enabled: bool = True
        ):
    token = Token(
        tokenid=jti, userid=user_id,
        appid=app_id, is_enabled=is_enabled
        )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


async def get_db_token(db: Session, jti: str):
    token = db.query(Token).filter(Token.tokenid == jti).first()
    return token


async def update_db_token(db: Session, jti: str, is_enabled: bool):
    token = db.query(Token).filter(Token.tokenid == jti).first()
    if token:
        token.is_enabled = is_enabled
        db.commit()
        db.refresh(token)
        return token
    return None
