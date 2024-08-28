from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas
from ...database import get_db
from ...cruds.token import (
    get_db_token_by_refresh_token, recrate_token,
    update_db_token
    )

router = APIRouter(
    prefix="/token/code",
    tags=["token/code"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=schemas.Token)
async def create_code(code: str, db: Session = Depends(get_db)):
    # リフレッシュトークンを検索
    token: schemas.DBToken | None = await get_db_token_by_refresh_token(
        db, code
        )
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    # トークンを無効化
    await update_db_token(db, code, False)
    # トークンを再生成
    new_access_token, new_refresh_token = await recrate_token(
        token.user_id, token.client_id, token.scope, db
    )
    return {
        "access_token": new_access_token[0],
        "refresh_token": new_refresh_token[0]
        }
