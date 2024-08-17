from pydantic import BaseModel, Field
from typing import List


class BaseFlag(BaseModel):
    """
    flagの基底クラス
    """
    id: int
    name: str = Field(..., min_length=1, max_length=32)
    users: List[int] = Field(default=[])


class Flag(BaseFlag):
    """
    flagの詳細クラス
    """
    description: str = Field(..., max_length=1024)
    image_url: str = Field(..., max_length=256)
    users: List[int] = Field(default=[])
    logs: List[int] = Field(default=[])


class CreateFlag(BaseFlag):
    """
    flagの作成クラス
    """

    class Config:
        model_validate = True
