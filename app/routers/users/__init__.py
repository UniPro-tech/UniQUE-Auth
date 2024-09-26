from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...cruds.user import get_user_by_name, get_user_by_email, create_user
from ...schemas import (
    User as UserSchema,
    CreateUser as CreateUserSchema
)
from ...database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=UserSchema)
async def create_users(
            new_user: CreateUserSchema,
            session: Session = Depends(get_db)
        ):
    user_check = get_user_by_email(session, new_user.email)
    if user_check:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_check = get_user_by_name(session, new_user.name)
    if user_check:
        raise HTTPException(status_code=400, detail="Name already registered")

    user = await create_user(new_user, session)

    return UserSchema(user)
