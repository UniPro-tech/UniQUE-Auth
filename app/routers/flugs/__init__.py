from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas import (
    Me as MeSchema,
    Flag as FlagSchema,
    CreateFlag as CreateFlagSchema,
    UpdataFlag as UpdateFlagSchema
)
from ...cruds.token import verify_token
from ...cruds.flag import (
    create_flag,
    get_flag_by_id,
    update_flag,
    delete_flag
)
from ...database import get_db

router = APIRouter(
    prefix="/flags",
    tags=["flags"],
)


@router.post("/", response_model=FlagSchema)
async def create_flags(
            flag: CreateFlagSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    # TODO: 権限周りの処理は後ほど記述

    new_flag: FlagSchema = await create_flag(db=db, flag=flag)

    return new_flag


@router.get("/{flag_id}", response_model=FlagSchema)
async def read_flags(
            flag_id: int,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    # TODO: 権限周りの処理は後ほど記述

    flag: FlagSchema = await get_flag_by_id(db, flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flag


@router.patch("/{flag_id}", response_model=FlagSchema)
async def edit_flags(
            flag: UpdateFlagSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)):
    # TODO: 権限周りの処理は後ほど記述

    flag: FlagSchema = await update_flag(db, flag.id, flag)
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flag


@router.delete("/{flag_id}", response_model=FlagSchema)
async def delete_flags(
            flag_id: int,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)):
    # TODO: 権限周りの処理は後ほど記述

    await delete_flag(db, flag_id)

    return {"message": "Flag deleted successfully"}
