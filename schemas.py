from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=15, regex=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., regex=r'/^[a-z\d][\w.-]*@[\w.-]+\.[a-z\d]+$/i')


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=30, regex=r'/^(?=.*?[a-z])(?=.*?\d)[a-z\d]{8,20}$/i')


class User(UserBase):
    id: int
    name: str = Field(..., min_length=1, max_length=32, regex=r'^[a-zA-Z0-9_]+$')
    created_at: datetime

    class Config:
        orm_mode = True
