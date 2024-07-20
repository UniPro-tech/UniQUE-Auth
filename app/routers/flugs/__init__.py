from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/flugs",
    tags=["flugs"],
)


@router.post("/", response_model=schemas.Flug)
async def create_flug(flug: schemas.FlugCreate, db: Session = Depends(get_db)):
    pass


@router.get("/{flug_id}", response_model=schemas.Flug)
async def read_flug(flug_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{flug_id}", response_model=schemas.Flug)
async def edit_flug(flug_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{flug_id}", response_model=schemas.Flug)
async def delete_flug(flug_id: int, db: Session = Depends(get_db)):
    pass
