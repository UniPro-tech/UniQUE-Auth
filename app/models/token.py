import os
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
        client_id: int, user_id: int,
        scope: List[str], exp: int
        ):
    payload = {
        'iss': 'https://portal.uniproject-tech.net',
        'sub': client_id,
        'user': user_id,
        'exp': exp,
        'scope': scope
    }

    return generate_token(payload=payload)


def generate_refresh_token(
        token_id: int, exp: int
        ):
    payload = {
        'iss': 'https://portal.uniproject-tech.net',
        'sub': token_id,
        'exp': exp,
    }

    return generate_token(payload=payload)
