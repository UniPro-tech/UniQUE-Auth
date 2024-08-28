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
            'exp': token.exp,
            'iat': token.iat,
            'jti': uuid,
        },
        key=__SQLALCHEMY_DATABASE_URI,
        algorithm=token.alg,
        headers={'alg': token.alg, 'typ': token.typ}
    )
    return refresh_token, uuid


async def add_db_token(
        db: Session, dbtoken: schemas.DBToken
        ):
    token = Token(
        **dbtoken.model_dump()
        )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


async def get_db_token_by_refresh_token(
        db: Session, refresh_token_id: str
        ) -> schemas.DBToken | None:
    # リフレッシュトークンからトークンを取得する
    token = (
        db.query(Token)
        .filter(Token.refresh_token_id == refresh_token_id)
        .first()
        )
    if token:
        return None
    return token


async def update_db_token(
        db: Session, jti: str, is_enabled: bool, is_refresh: bool = True
        ):
    # トークンを無効化する
    if is_refresh:
        token = db.query(Token).filter(Token.refresh_token_id == jti).first()
    else:
        token = db.query(Token).filter(Token.acsess_token_id == jti).first()
    if token:
        token.is_enabled = is_enabled
        db.commit()
        db.refresh(token)
        return token
    return None


async def recrate_token(user_id: int, client_id: int, scope: int, db: Session):
    access_token_data = schemas.AccessToken(
        sub=user_id,
        iss=client_id,
        scope=scope
    )
    access_token = create_access_token(access_token_data)

    refresh_token_data = schemas.RefreshToken()
    refresh_token = create_refresh_token(refresh_token_data)

    await add_db_token(
        db, acsess_token_id=access_token[1],
        refresh_token_id=refresh_token[1],
        scope=scope, user_id=user_id, client_id=client_id
    )

    return access_token, refresh_token


def decode_token(
        token: str, is_acsess_token: bool = True
        ) -> schemas.AccessToken | schemas.RefreshToken:
    plane_token_data = jwt.decode(
        token, key=__SQLALCHEMY_DATABASE_URI, algorithms=['HS256']
        )
    if is_acsess_token:
        token_data = schemas.AccessToken(**plane_token_data)
    else:
        token_data = schemas.RefreshToken(**plane_token_data)

    return token_data
