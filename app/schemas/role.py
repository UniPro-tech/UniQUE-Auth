from pydantic import BaseModel, Field
from typing import List


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)


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
    parmission_bit: int = Field(default=0)
    display_name: str = Field(..., min_length=3, max_length=30)

    class Config:
        model_validate = True


class UpdateRole(RoleBase):
    display_name: str = Field(..., min_length=3, max_length=30)
    discription: str = Field(..., max_length=255)
    parmission_bit: int = Field(default=0)
    sort: int = Field(default=0)
    is_enable: bool = Field(default=True)

    class Config:
        model_validate = True
