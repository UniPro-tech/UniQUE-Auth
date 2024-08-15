from pydantic import BaseModel, Field
from typing import List


class RoleBase(BaseModel):
    id:  int
    name: str = Field(..., max_length=100)
    parmission_bit: int = Field(default=0)
    sort: int = Field(default=0)


class Role(RoleBase):
    description: str = Field(..., max_length=255)
    # 多体多のリレーション
    users: List[int] = Field(default=[])
    logs: List[int] = Field(default=[])

    class Config:
        model_validate = True


class CreateRole(RoleBase):
    description: str = Field(..., max_length=255)

    class Config:
        model_validate = True
