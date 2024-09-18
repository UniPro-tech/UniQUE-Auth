from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...schemas import (
    Me as MeSchema,
    Flag as FlagSchema,
    CreateFlag as CreateFlagSchema,
)
from ...cruds.token import verify_token
from ...cruds.flag import create_flag
from ...database import get_db

router = APIRouter(
    prefix="/flags",
    tags=["flags"],
)


@router.post("/", response_model=FlagSchema)
async def create_flag(
            flag: CreateFlagSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    #TODO: 権限周りの処理は後ほど記述

    new_flag: FlagSchema = await crud.create_flag(db=db, flag=flag)


@router.get("/{flag_id}", response_model=FlagSchema)
async def read_flag(flag_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{flag_id}", response_model=FlagSchema)
async def edit_flag(flag_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{flag_id}", response_model=FlagSchema)
async def delete_flag(flag_id: int, db: Session = Depends(get_db)):
    pass
