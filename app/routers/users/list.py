from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/users/list",
)


@router.get("/", response_model=schemas.UserList)
async def read_users(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
        ):
    pass
