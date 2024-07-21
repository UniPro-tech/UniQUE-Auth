from typing import List
from pydantic import BaseModel, Field


class BaseToken(BaseModel):
    alg: str = Field(..., default="HS256")
    typ: str = Field(..., default="JWT")
    iss: str = Field(..., default="https://portal.uniproject-tech.net")
    exp: int = Field(..., description="有効期限")
    sub: int = Field(..., description="ClientID")
    user: int = Field(..., description="UserID")


class AccessToken(BaseToken):
    scope: List[str] = Field(..., description="permissions")

    class Config:
        orm_mode = True


class RefreshToken(BaseToken):

    class Config:
        orm_mode = True
