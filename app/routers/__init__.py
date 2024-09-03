from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..cruds.user import get_user_by_name, get_user_by_email, create_user
from .. import schemas
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.CreateUser)
async def create_users(
            user: schemas.CreateUser,
            db: Session = Depends(get_db)
        ):
    user_check = get_user_by_email(db, user.email)
    if user_check:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_check = get_user_by_name(db, user.name)
    if user_check:
        raise HTTPException(status_code=400, detail="Name already registered")

    user_data = schemas.CreateUser(
        name=user.name,
        email=user.email,
        passwd=user.hash_password
    )

    user = await create_user(user_data, db)

    return user
