from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db

router = APIRouter(
    prefix="/apps",
    tags=["apps", "users"],
)


@router.get("/{app_id}/users", response_model=schemas.User)
async def read_users(app_id: int, db: Session = Depends(get_db)):
    return crud.get_users_by_app_id(db, app_id)
