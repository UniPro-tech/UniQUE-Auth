from time import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.cruds.token import (
    recrate_token, decode_token,
    get_db_token_by_token, update_db_token
)
from app.cruds.client import create_user_client
from app.cruds.user import get_user_by_email_passwd
from app.database import get_db
from app.utils.permission2bit import (
    generate_permissionbit,
)

router = APIRouter(
    prefix="/token",
    tags=["token"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Token)
async def create_token(
            email: str, passwd: str,
            scope: list[str], app_id: str,
            db: Session = Depends(get_db)
        ):
    user: schemas.User | False = get_user_by_email_passwd(
        db, email, passwd
    )

    if user:
        user_client_data = schemas.UsrClient(
            user=user.id
        )
        user_client: schemas.UserClient = create_user_client(
            db, user_client_data
        )

        _, recrate_token_data = await recrate_token(
            user.id, user_client.id, scope, db
        )
        return {
                "code": recrate_token_data[1],
            }

    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/", response_model=str)
async def verify_token(token: str, db: Session = Depends(get_db)):
    token: schemas.AccessToken = decode_token(token, is_acsess_token=True)
    token_data: schemas.DBToken = get_db_token_by_token(
        db, token.jti, is_refresh=False
        )
    if token.exp > time() or token_data.is_enabled:
        return HTTPException(status_code=401, detail="Token is invalid")

    return {"message": "Token is valid"}


@router.delete("/", response_model=str)
async def delete_token(token: str, db: Session = Depends(get_db)):
    token: schemas.AccessToken = decode_token(token, is_acsess_token=True)
    token_data: schemas.DBToken = get_db_token_by_token(
        db, token.jti, is_refresh=False
        )
    if token.exp > time() or token_data.is_enabled:
        return HTTPException(status_code=401, detail="Token is invalid")

    update_db_token(db, token.jti, False, is_refresh=False)

    return {"message": "Token is deleted"}
