from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, cruds
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.CreateUser)
async def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    cruds.user.get_user_by_email(db, user.email)
