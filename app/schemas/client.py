from pydantic import BaseModel, Field


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
    user: int = Field(..., title="ユーザーID")

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
    apps: int = Field(..., title="アプリID")

    class Config:
        model_validate = True
