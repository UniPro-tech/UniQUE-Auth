import os
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid_extensions import uuid7str
import jwt
from ..schemas import (
    DBToken as DBTokenSchema,
    Me as MeSchema,
    AccessToken as AccessTokenSchema,
    RefreshToken as RefreshTokenSchema
)
from ..database import get_db
from ..models import Token
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
    token = Token(**token.model_dump())
    session.add(token)
    session.commit()
    return token


async def get_db_token_by_token(
                session: Session, token_id: str, is_refresh: bool = True
            ) -> DBTokenSchema | None:
    # リフレッシュトークンからトークンを取得する
    if is_refresh:
        token = (
            session.query(Token)
            .filter(Token.refresh_token_id == token_id)
            .first()
        )
    else:
        token = (
            session.query(Token)
            .filter(Token.acsess_token_id == token_id)
            .first()
        )
    return token if token else None


async def update_db_token(
                session: Session, token: Token,
                is_enabled: bool = False
            ) -> DBTokenSchema | None:
    # トークンを無効化する
    token.is_enabled = is_enabled
    session.commit()
    session.refresh(token)
    return token


async def recrate_token(user_id: int, client_id: int, scope: int, db: Session):
    access_token_data = AccessTokenSchema(
        sub=user_id,
        iss=client_id,
        scope=scope
    )
    access_token = create_access_token(access_token_data)

    refresh_token_data = RefreshTokenSchema()
    refresh_token = create_refresh_token(refresh_token_data)

    await add_db_token(
        db, acsess_token_id=access_token[1],
        refresh_token_id=refresh_token[1],
        scope=scope, user_id=user_id, client_id=client_id
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
            db: Session = Depends(get_db)
        ) -> MeSchema | None:
    try:
        token_data = DBTokenSchema.model_validate(
            decode_token(token, is_acsess_token=False)
        )
        user = (
            db.query(DBTokenSchema)
            .filter(DBTokenSchema.user_id == token_data.user_id)
            .first()
        )
        return MeSchema.model_validate(user) if user else None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
