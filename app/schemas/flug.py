from pydantic import BaseModel, Field


class BaseFlug(BaseModel):
    """
    Flugの基底クラス
    """
    id: int
    name: str = Field(..., min_length=1, max_length=32)
    users: list[int] = Field(default=[])


class Flug(BaseFlug):
    """
    Flugの詳細クラス
    """
    description: str = Field(..., max_length=1024)
    image_url: str = Field(..., max_length=256)
    users: list[int] = Field(default=[])
    logs: list[int] = Field(default=[])


class CreateFlug(BaseFlug):
    """
    Flugの作成クラス
    """

    class Config:
        orm_mode = True
