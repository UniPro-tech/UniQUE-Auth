from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db
from ...cruds.token import verify_token

router = APIRouter(
    prefix="/users/me",
    tags=["users"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=schemas.Me)
async def read_users_me(user: schemas.Me = Depends(verify_token())):
    return user


@router.patch("/", response_model=schemas.User)
async def update_users_me(db: Session = Depends(get_db)):
    pass
