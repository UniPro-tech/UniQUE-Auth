from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.responses import JSONResponse


class OAuthErrorCode(str, Enum):
    """OAuth 2.0 エラーコード (RFC6749)"""
    INVALID_REQUEST = "invalid_request"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    ACCESS_DENIED = "access_denied"
    UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"
    INVALID_SCOPE = "invalid_scope"
    SERVER_ERROR = "server_error"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"


class OIDCErrorCode(str, Enum):
    """OpenID Connect Core 1.0 追加エラーコード"""
    INTERACTION_REQUIRED = "interaction_required"
    LOGIN_REQUIRED = "login_required"
    ACCOUNT_SELECTION_REQUIRED = "account_selection_required"
    CONSENT_REQUIRED = "consent_required"
    INVALID_REQUEST_URI = "invalid_request_uri"
    INVALID_REQUEST_OBJECT = "invalid_request_object"
    REQUEST_NOT_SUPPORTED = "request_not_supported"
    REQUEST_URI_NOT_SUPPORTED = "request_uri_not_supported"
    REGISTRATION_NOT_SUPPORTED = "registration_not_supported"


class ErrorResponse(BaseModel):
    """RFC6749とOpenID Connect Core 1.0に準拠したエラーレスポンス"""
    error: str = Field(..., description="REQUIRED. Error code")
    error_description: Optional[str] = Field(None, description="OPTIONAL. Human-readable ASCII encoded error description")
    error_uri: Optional[str] = Field(None, description="OPTIONAL. URI of a web page with additional information about the error")
    state: Optional[str] = Field(None, description="REQUIRED if state parameter was present in the client authorization request")


def create_error_response(
    error: str,
    error_description: Optional[str] = None,
    error_uri: Optional[str] = None,
    state: Optional[str] = None,
    status_code: int = 400
) -> JSONResponse:
    """RFC6749とOpenID Connect Core 1.0に準拠したエラーレスポンスを生成"""
    response = ErrorResponse(
        error=error,
        error_description=error_description,
        error_uri=error_uri,
        state=state
    )
    return JSONResponse(
        status_code=status_code,
        content=response.dict(exclude_none=True),
        headers={
            "Cache-Control": "no-store",
            "Pragma": "no-cache"
        }
    )