from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..cruds.user import get_user_by_name, get_user_by_email, create_user
from .. import schemas
from ..database import get_db

router = APIRouter(
    prefix="/",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


class AuthorizeRequest(BaseModel):
    """ユーザー登録リクエスト"""
    scope: str  # REQUIRED
    response_type: str  # REQUIRED
    client_id: int  # REQUIRED
    redirect_uri: str  # REQUIRED
    state: str  # REQUIRED
    response_mode: Optional[str]  # OPTIONAL
    nonce: str  # OPTIONAL
    display: str  # OPTIONAL
    prompt: str  # OPTIONAL
    max_age: int  # OPTIONAL
    ui_locales: str  # OPTIONAL
    id_token_hint: str  # OPTIONAL
    login_hint: str  # OPTIONAL
    acr_values: str  # OPTIONAL

    def validate_required_fields(self) -> None:
        """AuthorizeRequestの必須フィールドを検証するメソッド"""
        # 必須フィールドのリスト
        # これらのフィールドはNoneであってはいけない
        required_fields = ["scope", "response_type", "client_id", "redirect_uri", "state"]
        for field in required_fields:
            if getattr(self, field) is None:
                raise ValueError(f"The field '{field}' is required and cannot be None.")
        
        # display変数の値を検証
        # displayはpage, popup, touch, wapのいずれかである必要がある
        display_values = ["page", "popup", "touch", "wap"]
        if self.display not in display_values:
            raise ValueError(f"The field 'display' must be one of {display_values}.")
        
        # prompt変数の値を検証
        # promptはnone, login, consent, select_accountのいずれかである必要がある
        prompt_values = ["none", "login", "consent", "select_account"]
        if self.prompt not in prompt_values:
            raise ValueError(f"The field 'prompt' must be one of {prompt_values}.")


@router.post("/authorize", response_model=schemas.User)
async def authorize(
            request: AuthorizeRequest,
            db: Session = Depends(get_db)
        ):
    """
    OIDC認証・認可リクエストエンドポイント
    """
    # リクエストパラメータの検証
    try:
        request.validate_required_fields()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ユーザーの認証


    # ユーザーの認可& トークンの発行

