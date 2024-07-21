from pydantic import BaseModel, Field


class UserBase(BaseModel):
    id: int
    name: str = Field(...,
                      min_length=3, max_length=16,
                      pattern=r'^[a-zA-Z0-9_]+$'
                      )
    display_name: str = Field(...,
                              min_length=1, max_length=32,
                              pattern=r'^[a-zA-Z0-9_]+$'
                              )
    is_bot: bool = Field(..., default=False)


class UserCreate(UserBase):
    email: str = Field(...,
                       min_length=1, max_length=256,
                       pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                       )
    password: str = Field(...,
                          min_length=8, max_length=256,
                          pattern=r'^[a-zA-Z0-9_]+$'
                          )


class User(UserBase):
    description: str = Field(..., max_length=1024)

    class Config:
        orm_mode = True


class Me(UserBase):
    email: str
    
    is_locked: bool
    created_at: int
    updated_at: int
    deleted_at: int


class Admin(UserBase):
    permission_bit: int
    is_enable: bool 
    is_enable: bool
    readonly: bool
    can_assign: bool
    sort: 0
