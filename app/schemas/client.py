from pydantic import BaseModel, Field
from typing import List


class BaseClient(BaseModel):
    """
    Clientの基底クラス
    Args:
        <id> <int>:
                クライアントID
        <type_> <str>:
                クライアントの種類(User, App)
        <is_enable> <bool>:
                有効かどうか
    """
    id: int
    type_: str
    is_enable: bool


class UserClient(BaseClient):
    """
    UserClientのスキーマ
    Args:
        <id> <int>:
                クライアントID
        <is_enable> <bool>:
                有効かどうか
    """
    users: List[int] = Field([], title="ユーザIDのリスト")

    class Config:
        model_validate = True


class AppClient(BaseClient):
    """
    AppClientのスキーマ
    Args:
        <id> <int>:
                クライアントID
        <is_enable> <bool>:
                有効かどうか
    """
    apps: List[int] = Field([], title="アプリケーションIDのリスト")

    class Config:
        model_validate = True
