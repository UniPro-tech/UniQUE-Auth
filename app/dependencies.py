from typing import Annotated

from fastapi import Header, HTTPException


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


async def verify_token(token: str):
    # Perform token verification logic here
    # Return True if the token is valid, False otherwise
    return True  # Placeholder logic, replace with actual token verification


async def validate_token(x_token: Annotated[str, Header()]):
    if not await verify_token(x_token):
        raise HTTPException(status_code=400, detail="Invalid token provided")
