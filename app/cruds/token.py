from app.models import (
    AccessToken,
    RefreshToken,
    IDToken
)


def create_access_token(session, token_hash, sub, iss, client_id, scope, iat, exp, status):
    token = AccessToken(
        token_hash=token_hash,
        sub=sub,
        iss=iss,
        client_id=client_id,
        scope=scope,
        iat=iat,
        exp=exp,
        status=status
    )
    session.add(token)
    session.commit()
    return token


def get_access_token_by_hash(session, token_hash):
    return session.query(AccessToken).filter_by(token_hash=token_hash).first()


def delete_access_token(session, token_hash):
    token = session.query(AccessToken).filter_by(token_hash=token_hash).first()
    if token:
        session.delete(token)
        session.commit()
        return True
    return False


def create_id_token(session, sub, iss, aud, iat, exp, auth_time=None, nonce=None):
    token = IDToken(
        sub=sub,
        iss=iss,
        aud=aud,
        iat=iat,
        exp=exp,
        auth_time=auth_time,
        nonce=nonce
    )
    session.add(token)
    session.commit()
    return token


def get_id_token_by_sub(session, sub):
    return session.query(IDToken).filter_by(sub=sub).all()


def delete_id_token(session, token_id):
    token = session.query(IDToken).filter_by(id=token_id).first()
    if token:
        session.delete(token)
        session.commit()
        return True
    return False


def create_refresh_token(session, token_hash, sub, client_id, iss, scope, iat, exp, status, rotated_from_id=None):
    token = RefreshToken(
        token_hash=token_hash,
        sub=sub,
        client_id=client_id,
        iss=iss,
        scope=scope,
        iat=iat,
        exp=exp,
        status=status,
        rotated_from_id=rotated_from_id
    )
    session.add(token)
    session.commit()
    return token


def get_refresh_token_by_hash(session, token_hash):
    return session.query(RefreshToken).filter_by(token_hash=token_hash).first()


def delete_refresh_token(session, token_hash):
    token = session.query(RefreshToken).filter_by(token_hash=token_hash).first()
    if token:
        session.delete(token)
        session.commit()
        return True
    return False


"""
使用例
with Session() as session:
    # アクセストークンの作成
    new_access_token = create_access_token(
        session=session,
        token_hash="hashed_token_value",
        sub="user123",
        iss="auth_server",
        client_id="client_app",
        scope="read write",
        iat=datetime.utcnow(),
        exp=datetime.utcnow() + timedelta(hours=1),
        status=TokenStatus.ACTIVE
    )

    # アクセストークンの検索
    token = get_access_token_by_hash(session, "hashed_token_value")
    print(token)

    # アクセストークンの削除
    delete_success = delete_access_token(session, "hashed_token_value")
    print("Deleted:", delete_success)
"""