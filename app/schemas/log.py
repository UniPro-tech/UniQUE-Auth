from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer
import time


class BaseLog(BaseModel):
    """
    Logの基底クラス
    """
    id: int
    details: str = Field(..., max_length=1024)
    action_type: str = Field(..., max_length=32)
    timestamp = Column(Integer, default=int(time.time()))


class UserLog(BaseLog):
    """
    UserLogの詳細クラス
    """
    user_id: int

    class Config:
        orm_mode = True


class AppLog(BaseLog):
    """
    AppLogの詳細クラス
    """
    user_id: int
    app_id: int

    class Config:
        orm_mode = True


class FlugLog(BaseLog):
    """
    FlugLogの詳細クラス
    """
    user_id: int
    flug_id: int

    class Config:
        orm_mode = True


class RoleLog(BaseLog):
    """
    RoleLogの詳細クラス
    """
    user_id: int
    role_id: int

    class Config:
        orm_mode = True
