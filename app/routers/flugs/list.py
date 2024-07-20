from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db
from typing import List

router = APIRouter(
    prefix="/flugs/list",
    tags=["flugs", "list"],
)


@router.get("/", response_model=List[schemas.Flug])
async def read_flugs_list(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
        ):
    flugs = crud.flug.get_multi(db, skip=skip, limit=limit)
    return flugs
