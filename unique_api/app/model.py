from datetime import datetime
import uuid
from sqlalchemy import Boolean, ForeignKey, String, DateTime, Integer, func
from sqlalchemy.orm import mapped_column, relationship
from db import Base


# usersテーブル
class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    custom_id = mapped_column(String(255), ForeignKey("members.custom_id"), unique=True)
    created_at = mapped_column(DateTime, server_default=func.now())
    password_hash = mapped_column(String(255), nullable=False)
    email = mapped_column(String(255), ForeignKey("members.email"), unique=True)
    is_enable = mapped_column(Boolean)


# appsテーブル
class App(Base):
    __tablename__ = "apps"

    id = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # ← これが必要！
    )
    client_id = mapped_column(String(255), unique=True)
    client_secret = mapped_column(String(255))
    name = mapped_column(String(255))
    created_at = mapped_column(DateTime, server_default=func.now())
    is_enable = mapped_column(Boolean)
    redirect_uris = relationship("RedirectURI", cascade="all, delete-orphan")


# redirect_urisテーブル
class RedirectURI(Base):
    __tablename__ = "redirect_uris"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_id = mapped_column(String(255), ForeignKey("apps.id"))
    uri = mapped_column(String(255))
    created_at = mapped_column(DateTime, server_default=func.now())


# authsテーブル
class Auth(Base):
    __tablename__ = "auths"

    id = mapped_column(Integer, primary_key=True)
    auth_user_id = mapped_column(Integer, ForeignKey("users.id"))
    app_id = mapped_column(String(255), ForeignKey("apps.id"))
    created_at = mapped_column(DateTime, server_default=func.now())
    is_enable = mapped_column(Boolean)
    oidc_authorizations = relationship("OIDCAuthorization", back_populates="auth")
    oidc_tokens = relationship(
        "OIDCToken",
        secondary="oidc_authorizations",
        primaryjoin="Auth.id == OIDCAuthorization.auth_id",
        secondaryjoin="OIDCAuthorization.id == OIDCToken.oidc_authorization_id",
        viewonly=True,
        backref="auth",
    )


# oidc_authorizationsテーブル
class OIDCAuthorization(Base):
    __tablename__ = "oidc_authorizations"

    id = mapped_column(Integer, primary_key=True)
    auth_id = mapped_column(Integer, ForeignKey("auths.id"))
    code_id = mapped_column(Integer, ForeignKey("code.id"), unique=True)
    consent_id = mapped_column(Integer, ForeignKey("consents.id"), unique=True)
    created_at = mapped_column(DateTime, server_default=func.now())

    consent = relationship("Consent")
    code = relationship("Code", back_populates="oidc_authorization", uselist=False)
    auth = relationship("Auth", back_populates="oidc_authorizations")
    oidc_tokens = relationship("OIDCToken", back_populates="oidc_authorization")


# oidc_tokensテーブル
class OIDCToken(Base):
    __tablename__ = "oidc_tokens"

    id = mapped_column(Integer, primary_key=True)
    oidc_authorization_id = mapped_column(
        Integer, ForeignKey("oidc_authorizations.id"), unique=True
    )
    access_token_id = mapped_column(Integer, unique=True)
    refresh_token_id = mapped_column(Integer, unique=True)
    is_enable = mapped_column(Boolean)
    oidc_authorization = relationship("OIDCAuthorization", back_populates="oidc_tokens")


# codeテーブル
class Code(Base):
    __tablename__ = "code"

    id = mapped_column(Integer, primary_key=True)
    token = mapped_column(String(255))
    created_at = mapped_column(DateTime, server_default=func.now())
    exp = mapped_column(DateTime, nullable=False)
    is_enable = mapped_column(Boolean)

    # 外部キーを削除！逆参照だけにする
    oidc_authorization = relationship(
        "OIDCAuthorization", back_populates="code", uselist=False
    )


# access_tokensテーブル
class AccessToken(Base):
    __tablename__ = "access_tokens"

    id = mapped_column(Integer, primary_key=True)
    hash = mapped_column(String(255))
    type = mapped_column(String(255))
    scope = mapped_column(String(255))
    issued_at = mapped_column(DateTime)
    exp = mapped_column(DateTime)
    client_id = mapped_column(Integer)
    user_id = mapped_column(Integer)
    revoked = mapped_column(Boolean)


# refresh_tokensテーブル
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = mapped_column(Integer, primary_key=True)
    hash = mapped_column(String(255))
    type = mapped_column(String(255))
    scope = mapped_column(String(255))
    issued_at = mapped_column(DateTime)
    exp = mapped_column(DateTime)
    client_id = mapped_column(Integer)
    user_id = mapped_column(Integer)
    revoked = mapped_column(Boolean)


# consentsテーブル
class Consent(Base):
    __tablename__ = "consents"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope = mapped_column(String(255))
    is_enable = mapped_column(Boolean)


# sessionsテーブル
class Session(Base):
    __tablename__ = "sessions"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("users.id"))
    ip_address = mapped_column(String(255))
    user_agent = mapped_column(String(255))
    created_at = mapped_column(DateTime, server_default=func.now())
    is_enable = mapped_column(Boolean)


# membersテーブル
class Member(Base):
    __tablename__ = "members"

    id = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # ← これが必要！
    )
    name = mapped_column(String(255), nullable=False)
    email = mapped_column(String(255), unique=True)
    external_email = mapped_column(String(255), nullable=False)
    custom_id = mapped_column(String(255), unique=True, nullable=False)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime)
    joined_at = mapped_column(DateTime)
    is_enable = mapped_column(Boolean, nullable=False, default=True)
    period = mapped_column(String(255), nullable=False)
    system = mapped_column(Boolean, nullable=False, default=False)


# rolesテーブル
class Role(Base):
    __tablename__ = "roles"

    id = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # ← これが必要！
    )
    custom_id = mapped_column(String(255), unique=True)
    permissions = mapped_column(Integer, nullable=False, default=0)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime)
    is_enable = mapped_column(Boolean, nullable=False, default=True)
    system = mapped_column(Boolean, nullable=False, default=False)


# discordsテーブル
class Discord(Base):
    __tablename__ = "discords"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    discord_id = mapped_column(String(255), unique=True, nullable=False)
    member = mapped_column(String(255), ForeignKey("members.id"), nullable=False)


# member_roleテーブル
class MemberRole(Base):
    __tablename__ = "member_role"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    member = mapped_column(String(255), ForeignKey("members.id"), nullable=False)
    role = mapped_column(String(255), ForeignKey("roles.id"), nullable=False)


# member_appテーブル
class MemberApp(Base):
    __tablename__ = "member_app"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    app = mapped_column(String(255), ForeignKey("apps.id"))
    member = mapped_column(String(255), ForeignKey("members.id"))
