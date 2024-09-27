from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas import (
    Me as MeSchema,
    Role as RoleSchema
)
from ...cruds.token import verify_token
from ...cruds.role import get_roles
from ...database import get_db

router = APIRouter(
    prefix="/roles/list",
    tags=["roles", "list"],
)


@router.get("/", response_model=List[RoleSchema])
async def read_roles_list(
        user: MeSchema = Depends(verify_token),
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
        ):
    if user.scope not in "admin":
        roles = get_roles(db, skip=skip, limit=limit)
        return roles
    raise HTTPException(status_code=400, detail="Permission Denied")
