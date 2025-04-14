from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# すべての基本フィールドをまとめた共通スキーマ
class ClientBase(BaseModel):
    client_id: str = Field(..., max_length=100, description="ユニークなクライアントID")
    client_secret: str = Field(..., max_length=255, description="クライアントシークレット（ハッシュ化推奨）")
    client_type: str = Field(default="confidential", max_length=30, description='"confidential" or "public"')
    grant_types: str = Field(default="authorization_code", max_length=255, description="使用するgrantタイプ（スペース区切り）")
    response_types: str = Field(default="code", max_length=255, description="使用するレスポンスタイプ")
    token_endpoint_auth_method: str = Field(
        default="client_secret_basic", max_length=50, description="認証方式"
    )
    logo_uri: Optional[str] = Field(default=None, max_length=255, description="ロゴURI")
    client_uri: Optional[str] = Field(default=None, max_length=255, description="クライアント情報ページURI")
    tos_uri: Optional[str] = Field(default=None, max_length=255, description="利用規約URI")
    policy_uri: Optional[str] = Field(default=None, max_length=255, description="プライバシーポリシーURI")
    app_id: int = Field(..., description="外部キーとしてAppテーブルのID")
    user_id: int = Field(..., description="外部キーとしてUserテーブルのID")

    model_config = ConfigDict(from_attributes=True)


# 作成用スキーマ（IDや作成日時などは未設定）
class ClientCreate(ClientBase):
    pass


# 更新用スキーマ：更新可能なフィールドのみ（IDや作成日時などは除外）
class ClientUpdate(BaseModel):
    # 必要に応じて、更新可能な項目だけOptionalにする
    client_secret: Optional[str] = Field(None, max_length=255)
    client_type: Optional[str] = Field(None, max_length=30)
    grant_types: Optional[str] = Field(None, max_length=255)
    response_types: Optional[str] = Field(None, max_length=255)
    token_endpoint_auth_method: Optional[str] = Field(None, max_length=50)
    logo_uri: Optional[str] = Field(None, max_length=255)
    client_uri: Optional[str] = Field(None, max_length=255)
    tos_uri: Optional[str] = Field(None, max_length=255)
    policy_uri: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


# 読み出し用スキーマ（DBに登録済みのレコードをそのまま表現）
class ClientRead(ClientBase):
    id: int = Field(..., description="自動採番された主キー")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)

    class Config:
        model_validate = True
