# sqlacodegen "mysql://api:P%40ssw0rd@127.0.0.1:8336/devdb"
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import ulid


class Base(DeclarativeBase):
    pass


# ULIDを生成する関数
# 残念ながらMySQLのStoredFunctionでULIDの関数を使ってもこっちから呼び出せない。
def generate_ulid():
    return str(ulid.new())


class Apps(Base):
    __tablename__ = "apps"
    __table_args__ = (Index("client_id", "client_id", unique=True),)

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    client_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    client_secret: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    name: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    auths: Mapped[List["Auths"]] = relationship("Auths", back_populates="app")
    redirect_uris: Mapped[List["RedirectUris"]] = relationship(
        "RedirectUris", back_populates="app"
    )
    user_app: Mapped[List["UserApp"]] = relationship("UserApp", back_populates="app")


class Code(Base):
    __tablename__ = "code"
    __table_args__ = (Index("token", "token", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    exp: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP)

    oidc_authorizations: Mapped[List["OidcAuthorizations"]] = relationship(
        "OidcAuthorizations", back_populates="code"
    )


class Consents(Base):
    __tablename__ = "consents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_enable: Mapped[Optional[int]] = mapped_column(TINYINT(1))

    oidc_authorizations: Mapped[List["OidcAuthorizations"]] = relationship(
        "OidcAuthorizations", back_populates="consent"
    )


class Roles(Base):
    __tablename__ = "roles"
    __table_args__ = (
        Index("custom_id", "custom_id", unique=True),
        {"comment": "ロール情報"},
    )

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    permissions: Mapped[int] = mapped_column(Integer, server_default=text("'0'"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    system: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
    custom_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP)

    user_role: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="role"
    )


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("custom_id", "custom_id", unique=True),
        Index("email", "email", unique=True),
        Index("idx_users_custom_id", "custom_id"),
    )

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    name: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    password_hash: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    external_email: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    period: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_system: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
    custom_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    email: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    joined_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_enable: Mapped[Optional[int]] = mapped_column(
        TINYINT(1), server_default=text("'1'")
    )

    auths: Mapped[List["Auths"]] = relationship("Auths", back_populates="auth_user")
    discords: Mapped[List["Discords"]] = relationship("Discords", back_populates="user")
    sessions: Mapped[List["Sessions"]] = relationship("Sessions", back_populates="user")
    user_app: Mapped[List["UserApp"]] = relationship("UserApp", back_populates="user")
    user_role: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="user"
    )


class Auths(Base):
    __tablename__ = "auths"
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="auths_ibfk_2"),
        ForeignKeyConstraint(["auth_user_id"], ["users.id"], name="auths_ibfk_1"),
        Index("app_id", "app_id"),
        Index("auth_user_id", "auth_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    app_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    app: Mapped["Apps"] = relationship("Apps", back_populates="auths")
    auth_user: Mapped["Users"] = relationship("Users", back_populates="auths")
    oidc_authorizations: Mapped[List["OidcAuthorizations"]] = relationship(
        "OidcAuthorizations", back_populates="auth"
    )


class Discords(Base):
    __tablename__ = "discords"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="discords_ibfk_1"),
        Index("discord_id", "discord_id", unique=True),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discord_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))

    user: Mapped["Users"] = relationship("Users", back_populates="discords")


class RedirectUris(Base):
    __tablename__ = "redirect_uris"
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="redirect_uris_ibfk_1"),
        Index("app_id", "app_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    uri: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    app: Mapped["Apps"] = relationship("Apps", back_populates="redirect_uris")


class Sessions(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="sessions_ibfk_1"),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    ip_address: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    user_agent: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    user: Mapped["Users"] = relationship("Users", back_populates="sessions")


class UserApp(Base):
    __tablename__ = "user_app"
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="user_app_ibfk_1"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_app_ibfk_2"),
        Index("app_id", "app_id"),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    user_id: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"))

    app: Mapped[Optional["Apps"]] = relationship("Apps", back_populates="user_app")
    user: Mapped[Optional["Users"]] = relationship("Users", back_populates="user_app")


class UserRole(Base):
    __tablename__ = "user_role"
    __table_args__ = (
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="user_role_ibfk_2"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_role_ibfk_1"),
        Index("role_id", "role_id"),
        Index("user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    role_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))

    role: Mapped["Roles"] = relationship("Roles", back_populates="user_role")
    user: Mapped["Users"] = relationship("Users", back_populates="user_role")


class OidcAuthorizations(Base):
    __tablename__ = "oidc_authorizations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["auth_id"], ["auths.id"], name="oidc_authorizations_ibfk_1"
        ),
        ForeignKeyConstraint(
            ["code_id"], ["code.id"], name="oidc_authorizations_ibfk_3"
        ),
        ForeignKeyConstraint(
            ["consent_id"], ["consents.id"], name="oidc_authorizations_ibfk_2"
        ),
        Index("auth_id", "auth_id"),
        Index("code_id", "code_id", unique=True),
        Index("consent_id", "consent_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_id: Mapped[int] = mapped_column(Integer)
    code_id: Mapped[int] = mapped_column(Integer)
    consent_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    auth: Mapped["Auths"] = relationship("Auths", back_populates="oidc_authorizations")
    code: Mapped["Code"] = relationship("Code", back_populates="oidc_authorizations")
    consent: Mapped["Consents"] = relationship(
        "Consents", back_populates="oidc_authorizations"
    )
    oidc_tokens: Mapped[List["OidcTokens"]] = relationship(
        "OidcTokens", back_populates="oidc_authorization"
    )


class OidcTokens(Base):
    __tablename__ = "oidc_tokens"
    __table_args__ = (
        ForeignKeyConstraint(
            ["oidc_authorization_id"],
            ["oidc_authorizations.id"],
            name="oidc_tokens_ibfk_1",
        ),
        Index("access_token_id", "access_token_id", unique=True),
        Index("oidc_authorization_id", "oidc_authorization_id", unique=True),
        Index("refresh_token_id", "refresh_token_id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    oidc_authorization_id: Mapped[int] = mapped_column(Integer)
    access_token_id: Mapped[int] = mapped_column(Integer)
    refresh_token_id: Mapped[int] = mapped_column(Integer)
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))

    oidc_authorization: Mapped["OidcAuthorizations"] = relationship(
        "OidcAuthorizations", back_populates="oidc_tokens"
    )


class AccessTokens(OidcTokens):
    __tablename__ = "access_tokens"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id"], ["oidc_tokens.access_token_id"], name="access_tokens_ibfk_1"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    type: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    scope: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    issued_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)
    exp: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)
    client_id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), comment="アプリケーションID"
    )
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    revoked: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))


class RefreshTokens(OidcTokens):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id"], ["oidc_tokens.refresh_token_id"], name="refresh_tokens_ibfk_1"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    type: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    scope: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    issued_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)
    exp: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)
    client_id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), comment="アプリケーションID"
    )
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    revoked: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
