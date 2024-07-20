from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Role)
async def create_roles(db: Session = Depends(get_db)):
    pass


@router.get("/{role_id}", response_model=schemas.Role)
async def read_roles(role_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{role_id}", response_model=schemas.Role)
async def edit_roles(role_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{role_id}", response_model=schemas.Role)
async def delete_roles(role_id: int, db: Session = Depends(get_db)):
    pass
