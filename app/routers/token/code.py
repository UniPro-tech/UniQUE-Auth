from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/token/code",
    tags=["token/code"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=schemas.Token)
async def create_code(db: Session = Depends(get_db)):
    pass
