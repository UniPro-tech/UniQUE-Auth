from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    user_id: str = Field(...,
                         min_length=1, max_length=15,
                         pattern=r'^[a-zA-Z0-9_]+$'
                         )
    email: str = Field(...,
                       pattern=r'^[a-z\d][\w.-]*@[\w.-]+\.[a-z\d]+$/i'
                       )


class UserCreate(UserBase):
    password: str = Field(...,
                          min_length=8, max_length=30,
                          pattern=r'^[a-zA-Z0-9_@\-!?]+$',
                          )


class User(UserBase):
    id: int
    name: str = Field(...,
                      min_length=1, max_length=32,
                      pattern=r'^[a-zA-Z0-9_]+$'
                      )
    created_at: datetime

    class Config:
        from_attributes = True
