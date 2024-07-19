from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/users",
)


@router.post("/")
async def create_link_apps(db: Session = Depends(get_db)):
    pass
