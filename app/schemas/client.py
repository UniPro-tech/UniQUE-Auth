from pydantic import BaseModel, Field


class BaseClient(BaseModel):
    """
    Clientの基底クラス
    """
    pass


class Client(BaseClient):
    """
    Clientの詳細クラス
    """
    is_enable: bool = Field(default=True)
    user: int = Field(description="ユーザーID")
    app: int = Field(description="アプリケーションID")

    class Config:
        model_validate = True


class UpdataClient(BaseClient):
    """
    Clientの更新クラス
    """
    is_enable: bool

    class Config:
        model_validate = True
