from pydantic import BaseModel


class LoginRequest(BaseModel):
    custom_id: str
    password: str
    csrf_token: str
