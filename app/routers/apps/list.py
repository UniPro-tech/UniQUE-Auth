from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import crud, models, schemas
from ...database import get_db

router = APIRouter(
    prefix="/apps/list",
    tags=["apps", "list"],
)


@router.get("/", response_model=schemas.AppList)
async def read_apps_list(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db)
        ):
    """
    Retrieve apps.
    """
    apps = crud.app.get_multi(db, skip=skip, limit=limit)
    return apps
