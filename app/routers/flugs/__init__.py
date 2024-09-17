from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...schemas import (
    Me as MeSchema,
    Flag as FlagSchema,
    CreateFlag as CreateFlagSchema,
)
from ...cruds.token import verify_token
from ...database import get_db

router = APIRouter(
    prefix="/flugs",
    tags=["flugs"],
)


@router.post("/", response_model=FlagSchema)
async def create_flug(
            flug: CreateFlagSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    
    pass


@router.get("/{flug_id}", response_model=FlagSchema)
async def read_flug(flug_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{flug_id}", response_model=FlagSchema)
async def edit_flug(flug_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{flug_id}", response_model=FlagSchema)
async def delete_flug(flug_id: int, db: Session = Depends(get_db)):
    pass
