from sqlalchemy.orm import Session
from uuid_extensions import uuid7str
import schemas
import schemas.token
from ..utils.token import (
    generate_access_token, generate_refresh_token,
    verified_token
    )


def create_access_token(
        db: Session, token: schemas.AccessToken
        ) -> str:
    uuid = uuid7str()
    # TODO:トークンをDBに保存する処理を追加する
    access_token = generate_access_token(
                                client_user_id=token.client_user_id,
                                client_app_id=token.client_app_id,
                                scope=token.scope,
                                exp=token.exp,
                                uuid=uuid
                                )
    return access_token


def create_refresh_token(
        db: Session, token: schemas.RefreshToken
        ) -> str:
    uuid = uuid7str()
    # TODO:トークンをDBに保存する処理を追加する
    refresh_token = generate_refresh_token(
                                token_id=token.token_id,
                                exp=token.exp,
                                client_user_id=token.client_user_id,
                                client_app_id=token.client_app_id,
                                uuid=uuid,
                                )
    return refresh_token


def validate_access_token(
        db: Session, token: str
        ) -> bool:

    decode_token = verified_token(token=token)
    if decode_token:
        pass
