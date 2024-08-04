from typing import List
import time
from pydantic import BaseModel, Field
from nanoid import generate


class BaseToken(BaseModel):
    alg: str = Field(default="HS256")
    typ: str = Field(default="JWT")
    iss: str = Field(default="https://portal.uniproject-tech.net")
    jti: int = Field(default=generate(), description="TokenID")
    sub: int = Field(..., description="ClientAppID")
    for_: int = Field(..., description="ClientUserID")


class AccessToken(BaseToken):
    scope: List[str] = Field(..., description="permissions")
    exp: int = Field(default=time.time() + 604800, description="有効期限")

    class Config:
        orm_mode = True


class RefreshToken(BaseToken):
    exp: int = Field(default=time.time() + 1209600, description="有効期限")

    class Config:
        orm_mode = True
