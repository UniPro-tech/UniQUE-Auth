from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db

router = APIRouter(
    prefix="/flugs",
    tags=["flugs", "roles"],
)


@router.get("/{flug_id}/roles", response_model=schemas.Role)
async def read_roles(flug_id: int, db: Session = Depends(get_db)):
    pass


@router.put("/{flug_id}/roles", response_model=schemas.Role)
async def update_roles(flug_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{flug_id}/roles", response_model=schemas.Role)
async def edit_roles(flug_id: int, db: Session = Depends(get_db)):
    pass
