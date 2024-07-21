import hashlib
import json
import time
from sqlalchemy.orm import Session
import models
import schemas
import schemas.token
from ..models.token import generate_access_token, generate_refresh_token


def create_access_token(
        db: Session, token: schemas.token.AccessToken
        ) -> str:

    access_token = generate_access_token(
                                client_id=token.sub,
                                scope=token.scope,
                                user_id=token.user,
                                exp=token.exp
                                )
    return access_token


def create_refresh_token(
        db: Session, token: schemas.token.RefreshToken
        ) -> str:

    refresh_token = generate_refresh_token(
                                token_id=token.token_id,
                                exp=token.exp
                                )
    return refresh_token
