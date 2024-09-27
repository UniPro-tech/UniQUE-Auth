from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas import (
    Me as MeSchema,
    Flag as FlagSchema
)
from ...cruds.token import verify_token
from ...cruds.flag import get_flags
from ...database import get_db
from typing import List

router = APIRouter(
    prefix="/flags/list",
    tags=["flags", "list"],
)


@router.get("/", response_model=List[FlagSchema])
async def read_flags_list(
        user: MeSchema = Depends(verify_token),
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
        ):
    if user.scope not in "admin":
        flags = get_flags(db, skip=skip, limit=limit)
        return flags
    raise HTTPException(status_code=400, detail="Permission Denied")
