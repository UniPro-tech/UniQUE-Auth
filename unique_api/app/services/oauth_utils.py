from fastapi import HTTPException
from typing import List
from pydantic import AnyHttpUrl


def validate_redirect_uri(
    requested_uri: AnyHttpUrl | None,
    registered_uris: List[str]
) -> str:
    if requested_uri is None:
        raise HTTPException(status_code=400, detail="Redirect URI not provided")

    if str(requested_uri) not in registered_uris:
        raise HTTPException(status_code=400, detail="Redirect URI not allowed")

    return str(requested_uri)
