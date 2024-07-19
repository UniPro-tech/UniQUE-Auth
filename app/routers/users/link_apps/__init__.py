from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db

router = APIRouter(
    prefix="/users",
)


async def read_link_apps(db: Session):
    pass


async def update_link_apps(db: Session):
    pass


async def delete_link_apps(db: Session):
    pass


@router.get("/{user_id}/link_apps")
async def userid_read_link_apps(db: Session = Depends(get_db)):
    return await read_link_apps(db=db)


@router.patch("/{user_id}/link_apps")
async def userid_update_link_apps(db: Session = Depends(get_db)):
    return await update_link_apps(db=db)


@router.delete("/{user_id}/link_apps")
async def userid_delete_link_apps(db: Session = Depends(get_db)):
    return await delete_link_apps(db=db)


@router.get("/@me/link_apps")
async def me_read_link_apps(db: Session = Depends(get_db)):
    return await read_link_apps(db=db)


@router.patch("/@me/link_apps")
async def me_update_link_apps(db: Session = Depends(get_db)):
    return await update_link_apps(db=db)


@router.delete("/@me/link_apps")
async def me_delete_link_apps(db: Session = Depends(get_db)):
    return await delete_link_apps(db=db)
