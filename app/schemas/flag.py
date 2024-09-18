from pydantic import BaseModel, Field
from typing import List


class BaseFlag(BaseModel):
    """
    flagの基底クラス
    """
    name: str = Field(..., min_length=1, max_length=32)


class Flag(BaseFlag):
    """
    flagの詳細クラス
    """
    id: int
    description: str = Field(..., max_length=1024)
    image_url: str = Field(..., max_length=256)
    is_enabled: bool = Field(default=True)
    can_assign: bool = Field(default=True)
    users: List[int] = Field(default=[])
    logs: List[int] = Field(default=[])

    class Config:
        model_validate = True


class CreateFlag(BaseFlag):
    """
    flagの作成クラス
    """

    class Config:
        model_validate = True
