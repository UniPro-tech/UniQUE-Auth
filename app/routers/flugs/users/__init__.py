from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db
from typing import List

router = APIRouter(
    prefix="/flugs",
    tags=["flugs", "users"],
)


@router.get("/{flug_id}/users", response_model=List[schemas.User])
async def read_users(flug_id: int, db: Session = Depends(get_db)):
    pass
