from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ... import schemas
from ...database import get_db
from ...cruds.token import verify_token
from ...cruds.user import update_user

router = APIRouter(
    prefix="/users/me",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=schemas.Me)
async def read_users_me(user: schemas.Me = Depends(verify_token())):
    return user


@router.patch("/", response_model=schemas.Me)
async def update_users_me(
        user: schemas.Me = Depends(verify_token()),
        new_user: schemas.UpdataMe = Depends(),
        db: Session = Depends(get_db)
        ):
    return update_user(db, user, new_user)
