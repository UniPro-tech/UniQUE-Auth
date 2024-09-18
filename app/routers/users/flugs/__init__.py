from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db

router = APIRouter(
    prefix="/users"
)


async def read_flags(db: Session):
    pass


async def update_flags(db: Session):
    pass


async def delete_flags(db: Session):
    pass


@router.get("/{user_id}/flags")
async def userid_read_flags(db: Session = Depends(get_db)):
    return await read_flags(db=db)


@router.patch("/{user_id}/flags")
async def userid_update_flags(db: Session = Depends(get_db)):
    return await update_flags(db=db)


@router.delete("/{user_id}/flags")
async def userid_delete_flags(db: Session = Depends(get_db)):
    return await delete_flags(db=db)


@router.get("/@me/flags")
async def me_read_flags(db: Session = Depends(get_db)):
    return await read_flags(db=db)


@router.patch("/@me/flags")
async def me_update_flags(db: Session = Depends(get_db)):
    return await update_flags(db=db)


@router.delete("/@me/flags")
async def me_delete_flags(db: Session = Depends(get_db)):
    return await delete_flags(db=db)
