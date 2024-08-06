from pydantic import BaseModel, Field


class BaseFlug(BaseModel):
    """
    Flugの基底クラス
    """
    id: int
    name: str = Field(..., min_length=1, max_length=32)
    description: str = Field(..., max_length=1024)
    image_url: str = Field(..., max_length=256)
