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
    id: int
    is_enable: bool
    user: int
    app: int

    class Config:
        model_validate = True


class UpdataClient(BaseClient):
    """
    Clientの更新クラス
    """
    is_enable: bool

    class Config:
        model_validate = True
