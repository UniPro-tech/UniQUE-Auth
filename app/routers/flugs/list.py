from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db
from typing import List

router = APIRouter(
    prefix="/flags/list",
    tags=["flags", "list"],
)


@router.get("/", response_model=List[schemas.flag])
async def read_flags_list(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
        ):
    flags = crud.flag.get_multi(db, skip=skip, limit=limit)
    return flags
