from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db
from ...dependencies import verify_token

router = APIRouter(
    prefix="/users/me",
    tags=["users"],
    dependencies=[Depends(verify_token)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=schemas.User)
async def read_users_me(db: Session = Depends(get_db)):
    pass


@router.patch("/", response_model=schemas.User)
async def update_users_me(db: Session = Depends(get_db)):
    pass
