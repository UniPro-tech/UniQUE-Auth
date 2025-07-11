from model import User, App, Auth, Consent, OIDCTokens, Token
from sqlalchemy.orm import Session
from pydantic import BaseModel


class StandardClalms(BaseModel):
    sub: str
    name: str
    given_name: str
    family_name: str
    nickname: str
    preferred_username: str
    profile: str
    picture: str
    website: str
    email: str
    email_verified: bool
    gender: str
    birthdate: str
    zoneinfo: str
    locale: str
    phone_number: str
    phone_number_verified: bool
    address: dict
    updated_at: int


class AddressClalm(BaseModel):
    formatted: str
    street_address: str
    locality: str
    region: str
    postal_code: str
    country: str
