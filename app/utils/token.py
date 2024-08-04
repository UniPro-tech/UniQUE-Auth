import os
import time
from typing import List
import jwt
from dotenv import load_dotenv

# .envファイルの内容を読み込見込む
load_dotenv(dotenv_path='../../.env')


__SQLALCHEMY_DATABASE_URI = os.environ['SECRET_KEY']


def generate_token(
            payload: dict,
            header: dict = {
                "alg": "HS256",
                "typ": "JWT"}
            ):
    global __SQLALCHEMY_DATABASE_URI
    encoded_jwt = jwt.encode(
        payload=payload, key=__SQLALCHEMY_DATABASE_URI,
        algorithm=header["alg"], headers=header
        )
    return encoded_jwt


def generate_access_token(
        client_app_id: int, client_user_id: int,
        scope: List[str], exp: int, uuid: str
        ):
    payload = {
        'iss': 'https://portal.uniproject-tech.net',
        'sub': client_app_id,  # AppのClientID
        'exp': exp,
        'iat': int(time.time()),
        'scope': scope,
        'for': client_user_id,
        'jti': uuid
    }

    return generate_token(payload=payload)


def generate_refresh_token(
        exp: int, uuid: str,
        client_user_id: int, client_app_id: int
        ):
    payload = {
        'iss': 'https://portal.uniproject-tech.net',
        'sub': client_app_id,
        'exp': exp,
        'iat': int(time.time()),
        'jti': uuid,
        'for': client_user_id
    }

    return generate_token(payload=payload)


def verified_token(token: str):
    global __SQLALCHEMY_DATABASE_URI

    decoded_jwt = jwt.decode(
            jwt=token, key=__SQLALCHEMY_DATABASE_URI,
            issuer="https://portal.uniproject-tech.net"
            )

    return True, decoded_jwt
