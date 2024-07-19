from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db

router = APIRouter(
    prefix="/users"
)


async def read_flugs(db: Session):
    pass


async def update_flugs(db: Session):
    pass


async def delete_flugs(db: Session):
    pass


@router.get("/{user_id}/flugs")
async def userid_read_flugs(db: Session = Depends(get_db)):
    return await read_flugs(db=db)


@router.patch("/{user_id}/flugs")
async def userid_update_flugs(db: Session = Depends(get_db)):
    return await update_flugs(db=db)


@router.delete("/{user_id}/flugs")
async def userid_delete_flugs(db: Session = Depends(get_db)):
    return await delete_flugs(db=db)


@router.get("/@me/flugs")
async def me_read_flugs(db: Session = Depends(get_db)):
    return await read_flugs(db=db)


@router.patch("/@me/flugs")
async def me_update_flugs(db: Session = Depends(get_db)):
    return await update_flugs(db=db)


@router.delete("/@me/flugs")
async def me_delete_flugs(db: Session = Depends(get_db)):
    return await delete_flugs(db=db)
