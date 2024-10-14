from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db

router = APIRouter(
    prefix="/flags",
    tags=["flags", "roles"],
)


@router.get("/{flag_id}/roles", response_model=schemas.Role)
async def read_roles(flag_id: int, db: Session = Depends(get_db)):
    pass


@router.put("/{flag_id}/roles", response_model=schemas.Role)
async def update_roles(flag_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{flag_id}/roles", response_model=schemas.Role)
async def edit_roles(flag_id: int, db: Session = Depends(get_db)):
    pass
