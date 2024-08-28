from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    acsess_token_id = Column(String, index=True)
    refresh_token_id = Column(String, index=True)
    user_id = Column(String, index=True)
    client_id = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
