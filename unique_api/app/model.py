from datetime import datetime
import uuid
from sqlalchemy import Boolean, ForeignKey, String, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


# usersテーブル
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    custom_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("members.custom_id"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), ForeignKey("members.email"), unique=True
    )
    is_enable: Mapped[bool] = mapped_column(Boolean)


# appsテーブル
class App(Base):
    __tablename__ = "apps"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # ← これが必要！
    )
    client_id: Mapped[str] = mapped_column(String(255), unique=True)
    client_secret: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_enable: Mapped[bool] = mapped_column(Boolean)
    redirect_uris = relationship("RedirectURI", cascade="all, delete-orphan")


# redirect_urisテーブル
class RedirectURI(Base):
    __tablename__ = "redirect_uris"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_id: Mapped[str] = mapped_column(String(255), ForeignKey("apps.id"))
    uri: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# authsテーブル
class Auth(Base):
    __tablename__ = "auths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    app_id: Mapped[str] = mapped_column(String(255), ForeignKey("apps.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_enable: Mapped[bool] = mapped_column(Boolean)


# oidc_authorizationsテーブル
class OIDCAuthorization(Base):
    __tablename__ = "oidc_authorizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_id: Mapped[int] = mapped_column(Integer, ForeignKey("auths.id"))
    code: Mapped[int] = mapped_column(Integer, unique=True)
    consent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("consents.id"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    consent = relationship("Consent")


# oidc_tokensテーブル
class OIDCToken(Base):
    __tablename__ = "oidc_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    oidc_authorization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("oidc_authorizations.id"), unique=True
    )
    access_token_id: Mapped[int] = mapped_column(Integer, unique=True)
    refresh_token_id: Mapped[int] = mapped_column(Integer, unique=True)
    is_enable: Mapped[bool] = mapped_column(Boolean)


# codeテーブル
class Code(Base):
    __tablename__ = "code"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    exp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_enable: Mapped[bool] = mapped_column(Boolean)


# access_tokensテーブル
class AccessToken(Base):
    __tablename__ = "access_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(255))
    scope: Mapped[str] = mapped_column(String(255))
    issued_at: Mapped[datetime] = mapped_column(DateTime)
    exp: Mapped[datetime] = mapped_column(DateTime)
    client_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    revoked: Mapped[bool] = mapped_column(Boolean)


# refresh_tokensテーブル
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(255))
    scope: Mapped[str] = mapped_column(String(255))
    issued_at: Mapped[datetime] = mapped_column(DateTime)
    exp: Mapped[datetime] = mapped_column(DateTime)
    client_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    revoked: Mapped[bool] = mapped_column(Boolean)


# consentsテーブル
class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope: Mapped[str] = mapped_column(String(255))
    is_enable: Mapped[bool] = mapped_column(Boolean)


# sessionsテーブル
class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    ip_address: Mapped[str] = mapped_column(String(255))
    user_agent: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_enable: Mapped[bool] = mapped_column(Boolean)


# membersテーブル
class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # ← これが必要！
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    external_email: Mapped[str] = mapped_column(String(255), nullable=False)
    custom_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    joined_at: Mapped[datetime] = mapped_column(DateTime)
    is_enable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    period: Mapped[str] = mapped_column(String(255), nullable=False)
    system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


# rolesテーブル
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # ← これが必要！
    )
    custom_id: Mapped[str] = mapped_column(String(255), unique=True)
    permissions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    is_enable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


# discordsテーブル
class Discord(Base):
    __tablename__ = "discords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    discord_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    member: Mapped[str] = mapped_column(
        String(255), ForeignKey("members.id"), nullable=False
    )


# member_roleテーブル
class MemberRole(Base):
    __tablename__ = "member_role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member: Mapped[str] = mapped_column(
        String(255), ForeignKey("members.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(255), ForeignKey("roles.id"), nullable=False
    )


# member_appテーブル
class MemberApp(Base):
    __tablename__ = "member_app"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app: Mapped[str] = mapped_column(String(255), ForeignKey("apps.id"))
    member: Mapped[str] = mapped_column(String(255), ForeignKey("members.id"))
