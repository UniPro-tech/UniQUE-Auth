from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...schemas import (
    App as AppSchema,
    CreateApp as AppCreateSchema,
    Me as MeSchema,
)
from ...cruds.app import create_app
from ...cruds.token import verify_token
from ...database import get_db

router = APIRouter(
    prefix="/apps",
    tags=["apps"],
)


@router.post("/", response_model=schemas.App)
async def create_app(
            app: AppCreateSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    
    return create_app(db=db, app=app)


@router.get("/{app_id}", response_model=schemas.App)
async def read_app(app_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{app_id}", response_model=schemas.App)
async def edit_app(app_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{app_id}", response_model=schemas.App)
async def delete_app(app_id: int, db: Session = Depends(get_db)):
    pass
