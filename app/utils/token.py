import os
import time
from typing import List
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv
from ..schemas.token import AccessToken, RefreshToken


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


def decode_token(token: str):
    global __SQLALCHEMY_DATABASE_URI
    try:
        decoded_jwt = jwt.decode(
            jwt=token, key=__SQLALCHEMY_DATABASE_URI,
            issuer="https://portal.uniproject-tech.net"
            )

        AccessToken()

        return decoded_jwt

    except ExpiredSignatureError:
        # トークンの有効期限が切れた場合の処理
        print("Token has expired")
        return None

    except InvalidTokenError:
        # その他のトークンの無効エラーの処理
        print("Invalid token")
        return None

    except Exception as e:
        # その他の予期しないエラーの処理
        print(f"An unexpected error occurred: {e}")
        return None


def verified_acsess_token(token: str):

    decode_token(token=token)
