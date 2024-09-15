from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...schemas import (
    App as AppSchema,
    CreateApp as AppCreateSchema,
    Me as MeSchema,
)
from ...cruds.app import create_app, add_admin_user_to_app, get_app_by_id
from ...cruds.token import verify_token
from ...database import get_db

router = APIRouter(
    prefix="/apps",
    tags=["apps"],
)


@router.post("/", response_model=schemas.App)
async def create_apps(
            app: AppCreateSchema,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    new_app: AppSchema = create_app(db=db, app=app)
    app: AppSchema = add_admin_user_to_app(db, new_app.id, user.id)
    return app


@router.get("/{app_id}", response_model=schemas.App)
async def read_app(
            app_id: int,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    app: AppSchema = get_app_by_id(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    elif app.is_enable is False:
        raise HTTPException(status_code=404, detail="App is not enable")
    return app


@router.patch("/{app_id}", response_model=schemas.App)
async def edit_app(app_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{app_id}", response_model=schemas.App)
async def delete_app(app_id: int, db: Session = Depends(get_db)):
    pass
