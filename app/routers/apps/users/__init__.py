from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....database import get_db
from ....cruds.token import verify_token
from ....schemas import (
    Me as MeSchema,
    User as UserSchema,
    App as AppSchema,
)
from ....cruds.app import get_app_by_id

router = APIRouter(
    prefix="/apps",
    tags=["apps", "users"],
)


@router.get("/{app_id}/users", response_model=List[UserSchema])
async def read_users(
            app_id: int,
            user: MeSchema = Depends(verify_token),
            db: Session = Depends(get_db)
        ):
    app: AppSchema = get_app_by_id(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    elif app.is_enable is False:
        raise HTTPException(status_code=404, detail="App is not enable")
    elif app.admin_users not in user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    return app.users
