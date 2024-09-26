from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...cruds.user import (
    get_users
)
from ...schemas import (
    Me as MeSchema,
    User as UserSchema
)
from ...cruds.token import verify_token
from ...database import get_db

router = APIRouter(
    prefix="/users/list",
    tags=["users/list"],
)


@router.get("/", response_model=List[UserSchema])
async def read_users(
        user: MeSchema = Depends(verify_token()),
        skip: int = 0, limit: int = 100,
        session: Session = Depends(get_db)
        ):
    if user.scope not in "admin":
        raise Exception("Permission Denied")

    users = get_users(session, skip, limit)

    return users
