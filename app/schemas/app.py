from pydantic import BaseModel, Field


class BaseApp(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    description: str = Field(..., max_length=1024)
    created_at: int
    updated_at: int
    deleted_at: int
    is_locked: bool
