from pydantic import BaseModel, AnyHttpUrl, Field
from typing import Optional


class AuthenticationRequest(BaseModel):
    # OAuth 2.0 Core
    response_type: str = Field(..., description="Type of response, e.g., 'code'")
    client_id: str = Field(..., description="Client ID issued during registration")
    redirect_uri: Optional[AnyHttpUrl] = Field(None, description="Redirection URI")
    scope: Optional[str] = Field(None, description="Space-separated list of scopes")
    state: Optional[str] = Field(None, description="Opaque value for maintaining state between request and callback")

    # PKCE
    code_challenge: Optional[str] = Field(None, description="PKCE: challenge string")
    code_challenge_method: Optional[str] = Field(None, description="PKCE: method used (e.g., S256)")

    # OpenID Connect
    nonce: Optional[str] = Field(None, description="String value to associate a client session with an ID token")
    display: Optional[str] = Field(None, description="Display mode: page, popup, touch, or wap")
    prompt: Optional[str] = Field(None, description="Prompt behavior: none, login, consent, select_account")
    max_age: Optional[int] = Field(None, description="Maximum authentication age in seconds")
    ui_locales: Optional[str] = Field(None, description="Space-separated list of preferred languages for UI")
    id_token_hint: Optional[str] = Field(None, description="Previously issued ID Token to hint about the user")
    acr_values: Optional[str] = Field(None, description="Requested Authentication Context Class Reference values")

    # Optional extension fields
    audience: Optional[str] = Field(None, description="Targeted resource server (optional extension)")

    class Config:
        extra = "allow"
