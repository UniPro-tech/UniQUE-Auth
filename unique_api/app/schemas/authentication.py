from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AuthenticationRequest(BaseModel):
    response_type: str = Field(
        ..., description="REQUIRED. Must be 'code' for Authorization Code Flow"
    )
    scope: str = Field(..., description="REQUIRED. Must include 'openid'")
    client_id: str = Field(..., description="REQUIRED. OAuth 2.0 Client Identifier")
    redirect_uri: str = Field(
        ..., description="REQUIRED. Redirection URI to return the response"
    )
    state: Optional[str] = Field(
        None, description="RECOMMENDED. Opaque value for maintaining state"
    )
    nonce: Optional[str] = Field(
        None,
        description="OPTIONAL. String value to associate client session with ID Token",
    )
    display: Optional[str] = Field(
        None, description="OPTIONAL. ASCII string value to specify UI display"
    )
    prompt: Optional[str] = Field(
        None,
        description="OPTIONAL. Space delimited, case sensitive list of ASCII values",
    )
    max_age: Optional[int] = Field(
        None, description="OPTIONAL. Maximum Authentication Age in seconds"
    )
    ui_locales: Optional[str] = Field(
        None, description="OPTIONAL. End-User's preferred languages and scripts for UI"
    )
    id_token_hint: Optional[str] = Field(
        None, description="OPTIONAL. Previously issued ID Token"
    )
    login_hint: Optional[str] = Field(
        None,
        description="OPTIONAL. Hint to the Authorization Server about the login identifier",
    )
    acr_values: Optional[str] = Field(
        None, description="OPTIONAL. Authentication Context Class Reference values"
    )

    @field_validator("scope")
    def validate_openid_scope(cls, v):
        if "openid" not in v.split():
            raise ValueError("scope must contain 'openid'")
        return v

    @field_validator("response_type")
    def validate_response_type(cls, v):
        if v != "code":
            raise ValueError("response_type must be 'code' for Authorization Code Flow")
        return v

    @field_validator("prompt")
    def validate_prompt(cls, v):
        if v:
            values = v.split()
            valid_values = {"none", "login", "consent", "select_account"}
            if not all(val in valid_values for val in values):
                raise ValueError("invalid prompt value")
            if "none" in values and len(values) > 1:
                raise ValueError("'none' cannot be combined with other values")
        return v
