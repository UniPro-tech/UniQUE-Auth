from pydantic import BaseModel, Field
from typing import List


class BaseFlug(BaseModel):
    """
    Flugの基底クラス
    """
    id: int
    name: str = Field(..., min_length=1, max_length=32)
    users: List[int] = Field(default=[])


class Flug(BaseFlug):
    """
    Flugの詳細クラス
    """
    description: str = Field(..., max_length=1024)
    image_url: str = Field(..., max_length=256)
    users: List[int] = Field(default=[])
    logs: List[int] = Field(default=[])


class CreateFlug(BaseFlug):
    """
    Flugの作成クラス
    """

    class Config:
        orm_mode = True
