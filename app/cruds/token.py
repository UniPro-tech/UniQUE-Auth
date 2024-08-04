from sqlalchemy.orm import Session
from uuid_extensions import uuid7str
from .. import schemas
from ..utils.token import (
    generate_access_token, generate_refresh_token,
    )
from ..schemas.token import BaseToken

def add_db_token(db: Session, token_data: BaseToken) -> BaseToken:
    
    db.add(token_data)
    
    return token_data
    


def create_access_token(
        token: schemas.AccessToken
        ) -> str:
    uuid = uuid7str()

    access_token = generate_access_token(
                                client_user_id=token.for_,
                                client_app_id=token.sub,
                                scope=token.scope,
                                exp=token.exp,
                                uuid=uuid
                                )
    return access_token


def create_refresh_token(
        token: schemas.RefreshToken
        ) -> str:
    uuid = uuid7str()
    # TODO:トークンをDBに保存する処理を追加する
    refresh_token = generate_refresh_token(
                                token_id=token.jti,
                                exp=token.exp,
                                client_user_id=token.for_,
                                client_app_id=token.sub,
                                uuid=uuid,
                                )
    return refresh_token

