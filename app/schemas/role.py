from pydantic import BaseModel, Field
from typing import List


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    parmission_bit: int = Field(default=0)


class Role(RoleBase):
    id:  int
    description: str = Field(..., max_length=255)
    # 多体多のリレーション
    users: List[int] = Field(default=[])
    logs: List[int] = Field(default=[])
    is_enable: bool = Field(default=True)
    parmission_bit: int = Field(default=0)

    class Config:
        model_validate = True


class CreateRole(RoleBase):

    class Config:
        model_validate = True


class UpdateRole(RoleBase):
    id: int
    discription: str = Field(..., max_length=255)
    sort: int = Field(default=0)
    is_enable: bool = Field(default=True)

    class Config:
        model_validate = True
