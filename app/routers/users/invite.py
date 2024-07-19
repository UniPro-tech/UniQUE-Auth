from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/users/invite",
)


@router.get("/", response_model=schemas.Invite)
async def read_invite(db: Session = Depends(get_db)):
    pass


@router.delete("/", response_model=schemas.Invite)
async def delete_invite(db: Session = Depends(get_db)):
    pass
