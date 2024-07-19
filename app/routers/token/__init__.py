from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/token",
    tags=["token"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=schemas.Token)
async def create_token(db: Session = Depends(get_db)):
    pass


@router.delete("/", response_model=schemas.Token)
async def delete_token(db: Session = Depends(get_db)):
    pass
