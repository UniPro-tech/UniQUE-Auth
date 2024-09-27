from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas import (
    App as AppSchema,
    Me as MeSchema
)
from ...database import get_db
from ...cruds.token import verify_token
from ...cruds.app import get_apps

router = APIRouter(
    prefix="/apps/list",
    tags=["apps", "list"],
)


@router.get("/", response_model=List[AppSchema])
async def read_apps_list(
        user: MeSchema = Depends(verify_token()),
        skip: int = 0, limit: int = 100,
        session: Session = Depends(get_db)
        ):
    if user.scope not in "admin":
        apps = get_apps(session, skip=skip, limit=limit)
        return apps
    raise HTTPException(status_code=400, detail="Permission Denied")
