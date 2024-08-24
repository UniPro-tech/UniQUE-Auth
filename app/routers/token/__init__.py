from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas
from ...cruds.token import create_access_token, create_refresh_token
from ...cruds.client import create_user_client
from ...cruds.user import get_user_by_email_passwd
from ...database import get_db
from ...utils.permission2bit import (
    generate_permissionbit,
)

router = APIRouter(
    prefix="/token",
    tags=["token"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Token)
async def create_token(
            email: str, passwd: str, scope: list[str],
            db: Session = Depends(get_db)
        ):
    try:
        user: schemas.User | False = get_user_by_email_passwd(
            db, email, passwd
        )
        permissionsbit = generate_permissionbit(*scope)
        if user:
            client: schemas.UserClient = create_user_client(db, user)
            access_token = schemas.AccessToken(
                sub=user.id,
                iss=client.id,
                scope=permissionsbit
            )
            access_token = create_access_token(user)
            refresh_token = create_refresh_token(user)
            return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=schemas.Token)
async def verify_token(db: Session = Depends(get_db)):
    pass


@router.delete("/", response_model=schemas.Token)
async def delete_token(db: Session = Depends(get_db)):
    pass
