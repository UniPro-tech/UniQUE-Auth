from sqlalchemy.orm import Session
import schemas
import schemas.token
from ..utils.token import generate_access_token, generate_refresh_token, verified_token


def create_access_token(
        db: Session, token: schemas.AccessToken
        ) -> str:

    access_token = generate_access_token(
                                client_id=token.sub,
                                scope=token.scope,
                                user_id=token.user,
                                exp=token.exp
                                )
    return access_token


def create_refresh_token(
        db: Session, token: schemas.RefreshToken
        ) -> str:

    refresh_token = generate_refresh_token(
                                token_id=token.token_id,
                                exp=token.exp
                                )
    return refresh_token


def validate_access_token(
        db: Session, token: str
        ) -> bool:

    decode_token = verified_token(token=token)
    if decode_token:
        
