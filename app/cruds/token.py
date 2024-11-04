import os
import time
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from uuid_extensions import uuid7str
import jwt
from app.schemas import (
    DBToken as DBTokenSchema,
    AccessToken as AccessTokenSchema,
    RefreshToken as RefreshTokenSchema
)
from app.cruds import (
    app as AppCruds,
    user as UserCruds
    )
from app.database import get_db
from app.models import (
    Token as TokenModel,
    User as UserModel,
    App as AppModel
)
from dotenv import load_dotenv


# .envファイルの内容を読み込見込む
load_dotenv(dotenv_path='../../.env')


__SQLALCHEMY_DATABASE_URI = os.environ['SECRET_KEY']

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(
                token: AccessTokenSchema
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
                token: RefreshTokenSchema
            ) -> str:
    uuid = uuid7str()
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
        session: Session, token: DBTokenSchema
        ):
    token = TokenModel(**token.model_dump())
    session.add(token)
    session.commit()
    return token


async def get_db_token_by_token(
                session: Session, token: str, is_refresh: bool = True
            ) -> TokenModel | None:
    # リフレッシュトークンからトークンを取得する
    if is_refresh:
        token = (
            session.scalar(
                select(TokenModel)
                .where(TokenModel.refresh_token == token)
            )
        )
    else:
        token = (
            session.scalar(
                select(TokenModel)
                .where(TokenModel.access_token == token)
            )
        )
    return token


async def update_db_token(
                session: Session, token: TokenModel,
                is_enabled: bool = False
            ) -> TokenModel:
    # トークンを無効化する
    token.is_enabled = is_enabled
    session.commit()
    session.refresh(token)
    return token


async def recrate_token(
                user_id: int, client_id: int,
                scope: List[str], session: Session
            ):
    access_token_data = AccessTokenSchema(
        sub=user_id,
        iss=client_id,
        scope=scope
    )
    access_token = create_access_token(access_token_data)

    refresh_token_data = RefreshTokenSchema()
    refresh_token = create_refresh_token(refresh_token_data)

    await add_db_token(
        session, acsess_token=access_token[0],
        refresh_token=refresh_token[0],
        client_id=client_id
    )

    return access_token, refresh_token


def decode_token(
        token: str, is_acsess_token: bool = True
        ) -> AccessTokenSchema | RefreshTokenSchema:
    plane_token_data = jwt.decode(
        token, key=__SQLALCHEMY_DATABASE_URI, algorithms=['HS256']
        )
    if is_acsess_token:
        token_data = AccessTokenSchema(**plane_token_data)
    else:
        token_data = RefreshTokenSchema(**plane_token_data)

    return token_data


async def verify_token(
            token: str = Depends(oauth2_scheme),
            session: Session = Depends(get_db)
        ) -> AppModel | UserModel | None:
    token_data = decode_token(token, is_acsess_token=False)
    token_db_data = await get_db_token_by_token(
                        session, token, is_refresh=False
                    )
    if token_data.exp < int(time.time()) and token_db_data.is_enabled:
        return None
    # Appの場合
    if token_db_data.refresh_token is None:
        return AppCruds.get_app_by_id(session, token_data.iss)
    # Userの場合
    return UserCruds.get_user_by_id(session, token_data.sub)
