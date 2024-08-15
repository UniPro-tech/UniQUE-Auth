import os
from sqlalchemy.orm import Session
from uuid_extensions import uuid7str
import jwt
from .. import schemas
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

    return access_token


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
    return refresh_token
