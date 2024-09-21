from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db
from typing import List

router = APIRouter(
    prefix="/flags",
    tags=["flags", "users"],
)


@router.get("/{flag_id}/users", response_model=List[schemas.User])
async def read_users(flag_id: int, db: Session = Depends(get_db)):
    pass
