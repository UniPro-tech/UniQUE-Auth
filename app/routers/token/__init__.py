from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas
from ...cruds.token import (
    recrate_token, decode_token
)
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
    user: schemas.User | False = get_user_by_email_passwd(
        db, email, passwd
    )

    if user:
        user_client_data = schemas.UserClient(
            user=user.id
        )
        user_client: schemas.UserClient = create_user_client(
            db, user_client_data
        )

        permissionsbit = generate_permissionbit(*scope)
        _, recrate_token_data = await recrate_token(
            user.id, user_client.id, permissionsbit, db
        )
        return {
                "code": recrate_token_data[1],
            }

    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/", response_model=str)
async def verify_token(token: str, db: Session = Depends(get_db)):
    token = decode_token(token, is_acsess_token=True)
    pass


@router.put("/", response_model=schemas.Token)
async def update_token(token: str, db: Session = Depends(get_db)):
    token = decode_token(token, is_acsess_token=False)
    pass


@router.delete("/", response_model=schemas.Token)
async def delete_token(db: Session = Depends(get_db)):
    pass
