from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/roles/list",
    tags=["roles", "list"],
)


@router.get("/", response_model=List[schemas.Role])
async def read_roles_list(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
        ):
    pass
