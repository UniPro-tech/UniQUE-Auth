from pydantic import BaseModel, Field
from typing import List


class BaseApp(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)


class CreateApp(BaseApp):

    class Config:
        model_validate = True


class UpdateApp(BaseApp):
    image_url: str = Field(..., max_length=256)
    description: str = Field(..., max_length=1024)

    class Config:
        model_validate = True


class App(BaseApp):
    id: int = Field()
    image_url: str = Field(..., max_length=256)
    description: str = Field(..., max_length=1024)
    verified: bool = Field(default=False)
    is_enable: bool
    admin_users: List[int] = Field(default=[])
    users: List[int] = Field(default=[])
    clients: List[int] = Field(default=[])