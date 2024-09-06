from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas
from ...cruds.user import (
    create_user,
    get_user_by_name,
    get_user_by_email
)
from ...database import get_db

router = APIRouter(
    prefix="/users",
)


@router.post("/", response_model=schemas.User)
async def user_create(user: schemas.CreateUser, db: Session = Depends(get_db)):

    serch_user = await get_user_by_name(db, user.name)
    serch_user = await get_user_by_email(db, user.email)
    if serch_user:
        raise HTTPException(status_code=400, detail="User already registered")
    if serch_user:
        raise HTTPException(status_code=400, detail="User already registered")

    user = await create_user(db, user)

    return user
