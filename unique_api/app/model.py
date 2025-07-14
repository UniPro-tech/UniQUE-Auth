from datetime import datetime
import uuid
from sqlalchemy import Boolean, ForeignKey, String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base
from datetime import datetime, timezone


# usersテーブル
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    custom_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("members.custom_id"), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), ForeignKey("members.email"), unique=True
    )
    is_enable: Mapped[bool] = mapped_column(Boolean)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    auths: Mapped[list["Auth"]] = relationship(back_populates="user")


# appsテーブル
class App(Base):
    __tablename__ = "apps"

    id = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # ← これが必要！
    )
    client_id: Mapped[str] = mapped_column(String(255), unique=True)
    client_secret: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_enable: Mapped[bool] = mapped_column(Boolean)

    redirect_uris: Mapped[list["RedirectURI"]] = relationship(back_populates="app")
    auths: Mapped[list["Auth"]] = relationship(back_populates="app")


# redirect_urisテーブル
class RedirectURI(Base):
    __tablename__ = "redirect_uris"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_id: Mapped[str] = mapped_column(String(255), ForeignKey("apps.id"))
    uri: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    app: Mapped["App"] = relationship(back_populates="redirect_uris")


# authsテーブル
class Auth(Base):
    __tablename__ = "auths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    app_id: Mapped[str] = mapped_column(String(255), ForeignKey("apps.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_enable: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship(back_populates="auths")
    app: Mapped["App"] = relationship(back_populates="auths")
    oidc_authorizations: Mapped[list["OIDCAuthorization"]] = relationship(
        back_populates="auth"
    )


# oidc_authorizationsテーブル
class OIDCAuthorization(Base):
    __tablename__ = "oidc_authorizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_id: Mapped[int] = mapped_column(Integer, ForeignKey("auths.id"))
    code: Mapped[int] = mapped_column(ForeignKey("code.id"), unique=True)
    content: Mapped[int] = mapped_column(Integer, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    code: Mapped["Code"] = relationship(back_populates="oidc_authorization")
    consent: Mapped["Consent"] = relationship(back_populates="oidc_authorization")
    auth: Mapped["Auth"] = relationship(back_populates="oidc_authorizations")
    oidc_token: Mapped["OIDCToken"] = relationship(back_populates="oidc_authorization")


# oidc_tokensテーブル
class OIDCToken(Base):
    __tablename__ = "oidc_tokens"

    id = mapped_column(Integer, primary_key=True)
    oidc_authorization_id = mapped_column(
        Integer, ForeignKey("oidc_authorizations.id"), unique=True
    )
    access_token_id: Mapped[int] = mapped_column(ForeignKey("access_tokens.id"), unique=True)
    refresh_token_id: Mapped[int] = mapped_column(ForeignKey("refresh_tokens.id"), unique=True)
    is_enable: Mapped[bool] = mapped_column(Boolean)

    access_token: Mapped["AccessToken"] = relationship(back_populates="oidc_token")
    refresh_token: Mapped["RefreshToken"] = relationship(back_populates="oidc_token")
    oidc_authorization: Mapped["OIDCAuthorization"] = relationship(
        back_populates="oidc_token"
    )


# codeテーブル
class Code(Base):
    __tablename__ = "code"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(Integer)
    exp: Mapped[int] = mapped_column(Integer)
    is_enable: Mapped[bool] = mapped_column(Boolean)

    oidc_authorization: Mapped["OIDCAuthorization"] = relationship(
        back_populates="code"
    )


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

    oidc_token: Mapped["OIDCToken"] = relationship(back_populates="access_token")


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

    oidc_token: Mapped["OIDCToken"] = relationship(back_populates="refresh_token")


# consentsテーブル
class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope: Mapped[str] = mapped_column(String(255))
    is_enable: Mapped[bool] = mapped_column(Boolean)

    oidc_authorization: Mapped["OIDCAuthorization"] = relationship(
        back_populates="consent"
    )


# sessionsテーブル
class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    ip_address: Mapped[str] = mapped_column(String(255))
    user_agent: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_enable: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship(back_populates="sessions")


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
    created_at = mapped_column(DateTime, server_default=datetime.now(timezone.utc), nullable=False)
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
    created_at = mapped_column(DateTime, server_default=datetime.now(timezone.utc), nullable=False)
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
