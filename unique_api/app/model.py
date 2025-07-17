# from sqlacodegen --generator sqlmodels "mysql://api:P%40ssw0rd@127.0.0.1:8336/devdb"
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlmodel import Field, Relationship, SQLModel


class Apps(SQLModel, table=True):
    __table_args__ = (Index("client_id", "client_id", unique=True),)

    id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "id",
            String(255, "utf8mb4_unicode_ci"),
            primary_key=True,
            server_default=text("'uuid()'"),
        ),
    )
    client_id: Optional[str] = Field(
        default=None, sa_column=Column("client_id", String(255, "utf8mb4_unicode_ci"))
    )
    client_secret: Optional[str] = Field(
        default=None,
        sa_column=Column("client_secret", String(255, "utf8mb4_unicode_ci")),
    )
    name: Optional[str] = Field(
        default=None, sa_column=Column("name", String(255, "utf8mb4_unicode_ci"))
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    is_enable: Optional[int] = Field(
        default=None, sa_column=Column("is_enable", TINYINT(1))
    )

    auths: List["Auths"] = Relationship(back_populates="app")
    member_app: List["MemberApp"] = Relationship(back_populates="apps")
    redirect_uris: List["RedirectUris"] = Relationship(back_populates="app")
    user_app: List["UserApp"] = Relationship(back_populates="app")


class Code(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    token: Optional[str] = Field(
        default=None, sa_column=Column("token", String(255, "utf8mb4_unicode_ci"))
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    exp: Optional[datetime] = Field(default=None, sa_column=Column("exp", TIMESTAMP))
    is_enable: Optional[int] = Field(
        default=None, sa_column=Column("is_enable", TINYINT(1))
    )

    oidc_authorizations: List["OidcAuthorizations"] = Relationship(
        back_populates="code"
    )


class Consents(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    scope: Optional[str] = Field(
        default=None, sa_column=Column("scope", String(255, "utf8mb4_unicode_ci"))
    )
    is_enable: Optional[int] = Field(
        default=None, sa_column=Column("is_enable", TINYINT(1))
    )

    oidc_authorizations: List["OidcAuthorizations"] = Relationship(
        back_populates="consent"
    )


class Members(SQLModel, table=True):
    __table_args__ = (
        Index("custom_id", "custom_id", unique=True),
        Index("email", "email", unique=True),
    )

    id: Optional[str] = Field(
        default=None,
        sa_column=Column("id", String(255, "utf8mb4_unicode_ci"), primary_key=True),
    )
    name: str = Field(sa_column=Column("name", String(255, "utf8mb4_unicode_ci")))
    external_email: str = Field(
        sa_column=Column("external_email", String(255, "utf8mb4_unicode_ci"))
    )
    custom_id: str = Field(
        sa_column=Column("custom_id", String(255, "utf8mb4_unicode_ci"))
    )
    created_at: datetime = Field(
        sa_column=Column("created_at", DateTime, server_default=text("(now())"))
    )
    is_enable: int = Field(sa_column=Column("is_enable", TINYINT(1)))
    period: str = Field(sa_column=Column("period", String(255, "utf8mb4_unicode_ci")))
    system: int = Field(sa_column=Column("system", TINYINT(1)))
    email: Optional[str] = Field(
        default=None, sa_column=Column("email", String(255, "utf8mb4_unicode_ci"))
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column("updated_at", DateTime)
    )
    joined_at: Optional[datetime] = Field(
        default=None, sa_column=Column("joined_at", DateTime)
    )

    member_app: List["MemberApp"] = Relationship(back_populates="members")
    member_role: List["MemberRole"] = Relationship(back_populates="members")


class Roles(SQLModel, table=True):
    __table_args__ = (
        Index("custom_id", "custom_id", unique=True),
        {"comment": "ロール情報"},
    )

    id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "id",
            String(255, "utf8mb4_unicode_ci"),
            primary_key=True,
            server_default=text("'uuid()'"),
        ),
    )
    permissions: int = Field(
        sa_column=Column("permissions", Integer, server_default=text("'0'"))
    )
    created_at: datetime = Field(
        sa_column=Column(
            "created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        )
    )
    is_enable: int = Field(
        sa_column=Column("is_enable", TINYINT(1), server_default=text("'1'"))
    )
    system: int = Field(
        sa_column=Column("system", TINYINT(1), server_default=text("'0'"))
    )
    custom_id: Optional[str] = Field(
        default=None, sa_column=Column("custom_id", String(255, "utf8mb4_unicode_ci"))
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column("updated_at", TIMESTAMP)
    )

    member_role: List["MemberRole"] = Relationship(back_populates="roles")
    user_role: List["UserRole"] = Relationship(back_populates="role")


class Users(SQLModel, table=True):
    __table_args__ = (
        Index("custom_id", "custom_id", unique=True),
        Index("email", "email", unique=True),
        Index("idx_users_custom_id", "custom_id"),
    )

    id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "id",
            String(255, "utf8mb4_unicode_ci"),
            primary_key=True,
            server_default=text("'uuid()'"),
        ),
    )
    name: str = Field(sa_column=Column("name", String(255, "utf8mb4_unicode_ci")))
    password_hash: str = Field(
        sa_column=Column("password_hash", String(255, "utf8mb4_unicode_ci"))
    )
    external_email: str = Field(
        sa_column=Column("external_email", String(255, "utf8mb4_unicode_ci"))
    )
    period: str = Field(sa_column=Column("period", String(255, "utf8mb4_unicode_ci")))
    is_system: int = Field(
        sa_column=Column("is_system", TINYINT(1), server_default=text("'0'"))
    )
    custom_id: Optional[str] = Field(
        default=None, sa_column=Column("custom_id", String(255, "utf8mb4_unicode_ci"))
    )
    email: Optional[str] = Field(
        default=None, sa_column=Column("email", String(255, "utf8mb4_unicode_ci"))
    )
    joined_at: Optional[datetime] = Field(
        default=None, sa_column=Column("joined_at", DateTime)
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column("updated_at", DateTime)
    )
    is_enable: Optional[int] = Field(
        default=None,
        sa_column=Column("is_enable", TINYINT(1), server_default=text("'1'")),
    )

    auths: List["Auths"] = Relationship(back_populates="auth_user")
    discords: List["Discords"] = Relationship(back_populates="user")
    sessions: List["Sessions"] = Relationship(back_populates="user")
    user_app: List["UserApp"] = Relationship(back_populates="user")
    user_role: List["UserRole"] = Relationship(back_populates="user")


class Auths(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="auths_ibfk_2"),
        ForeignKeyConstraint(["auth_user_id"], ["users.id"], name="auths_ibfk_1"),
        Index("app_id", "app_id"),
        Index("auth_user_id", "auth_user_id"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    auth_user_id: Optional[str] = Field(
        default=None,
        sa_column=Column("auth_user_id", String(255, "utf8mb4_unicode_ci")),
    )
    app_id: Optional[str] = Field(
        default=None, sa_column=Column("app_id", String(255, "utf8mb4_unicode_ci"))
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    is_enable: Optional[int] = Field(
        default=None, sa_column=Column("is_enable", TINYINT(1))
    )

    app: Optional["Apps"] = Relationship(back_populates="auths")
    auth_user: Optional["Users"] = Relationship(back_populates="auths")
    oidc_authorizations: List["OidcAuthorizations"] = Relationship(
        back_populates="auth"
    )


class Discords(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="discords_ibfk_1"),
        Index("discord_id", "discord_id", unique=True),
        Index("user_id", "user_id"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    discord_id: str = Field(
        sa_column=Column("discord_id", String(255, "utf8mb4_unicode_ci"))
    )
    user_id: str = Field(sa_column=Column("user_id", String(255, "utf8mb4_unicode_ci")))

    user: Optional["Users"] = Relationship(back_populates="discords")


class MemberApp(SQLModel, table=True):
    __tablename__ = "member_app"
    __table_args__ = (
        ForeignKeyConstraint(["app"], ["apps.id"], name="member_app_ibfk_1"),
        ForeignKeyConstraint(["member"], ["members.id"], name="member_app_ibfk_2"),
        Index("app", "app"),
        Index("member", "member"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    app: Optional[str] = Field(
        default=None, sa_column=Column("app", String(255, "utf8mb4_unicode_ci"))
    )
    member: Optional[str] = Field(
        default=None, sa_column=Column("member", String(255, "utf8mb4_unicode_ci"))
    )

    apps: Optional["Apps"] = Relationship(back_populates="member_app")
    members: Optional["Members"] = Relationship(back_populates="member_app")


class MemberRole(SQLModel, table=True):
    __tablename__ = "member_role"
    __table_args__ = (
        ForeignKeyConstraint(["member"], ["members.id"], name="member_role_ibfk_1"),
        ForeignKeyConstraint(["role"], ["roles.id"], name="member_role_ibfk_2"),
        Index("member", "member"),
        Index("role", "role"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    member: str = Field(sa_column=Column("member", String(255, "utf8mb4_unicode_ci")))
    role: str = Field(sa_column=Column("role", String(255, "utf8mb4_unicode_ci")))

    members: Optional["Members"] = Relationship(back_populates="member_role")
    roles: Optional["Roles"] = Relationship(back_populates="member_role")


class RedirectUris(SQLModel, table=True):
    __tablename__ = "redirect_uris"
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="redirect_uris_ibfk_1"),
        Index("app_id", "app_id"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    app_id: Optional[str] = Field(
        default=None, sa_column=Column("app_id", String(255, "utf8mb4_unicode_ci"))
    )
    uri: Optional[str] = Field(
        default=None, sa_column=Column("uri", String(255, "utf8mb4_unicode_ci"))
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )

    app: Optional["Apps"] = Relationship(back_populates="redirect_uris")


class Sessions(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="sessions_ibfk_1"),
        Index("user_id", "user_id"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    user_id: Optional[str] = Field(
        default=None, sa_column=Column("user_id", String(255, "utf8mb4_unicode_ci"))
    )
    ip_address: Optional[str] = Field(
        default=None, sa_column=Column("ip_address", String(255, "utf8mb4_unicode_ci"))
    )
    user_agent: Optional[str] = Field(
        default=None, sa_column=Column("user_agent", String(255, "utf8mb4_unicode_ci"))
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )
    is_enable: Optional[int] = Field(
        default=None, sa_column=Column("is_enable", TINYINT(1))
    )

    user: Optional["Users"] = Relationship(back_populates="sessions")


class UserApp(SQLModel, table=True):
    __tablename__ = "user_app"
    __table_args__ = (
        ForeignKeyConstraint(["app_id"], ["apps.id"], name="user_app_ibfk_1"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_app_ibfk_2"),
        Index("app_id", "app_id"),
        Index("user_id", "user_id"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    app_id: Optional[str] = Field(
        default=None, sa_column=Column("app_id", String(255, "utf8mb4_unicode_ci"))
    )
    user_id: Optional[str] = Field(
        default=None, sa_column=Column("user_id", String(255, "utf8mb4_unicode_ci"))
    )

    app: Optional["Apps"] = Relationship(back_populates="user_app")
    user: Optional["Users"] = Relationship(back_populates="user_app")


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    __table_args__ = (
        ForeignKeyConstraint(["role_id"], ["roles.id"], name="user_role_ibfk_2"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="user_role_ibfk_1"),
        Index("role_id", "role_id"),
        Index("user_id", "user_id"),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    user_id: str = Field(sa_column=Column("user_id", String(255, "utf8mb4_unicode_ci")))
    role_id: str = Field(sa_column=Column("role_id", String(255, "utf8mb4_unicode_ci")))

    role: Optional["Roles"] = Relationship(back_populates="user_role")
    user: Optional["Users"] = Relationship(back_populates="user_role")


class OidcAuthorizations(SQLModel, table=True):
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

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    auth_id: Optional[int] = Field(default=None, sa_column=Column("auth_id", Integer))
    code_id: Optional[int] = Field(default=None, sa_column=Column("code_id", Integer))
    consent_id: Optional[int] = Field(
        default=None, sa_column=Column("consent_id", Integer)
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
        ),
    )

    auth: Optional["Auths"] = Relationship(back_populates="oidc_authorizations")
    code: Optional["Code"] = Relationship(back_populates="oidc_authorizations")
    consent: Optional["Consents"] = Relationship(back_populates="oidc_authorizations")
    oidc_tokens: List["OidcTokens"] = Relationship(back_populates="oidc_authorization")


class OidcTokens(SQLModel, table=True):
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

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    oidc_authorization_id: Optional[int] = Field(
        default=None, sa_column=Column("oidc_authorization_id", Integer)
    )
    access_token_id: Optional[int] = Field(
        default=None, sa_column=Column("access_token_id", Integer)
    )
    refresh_token_id: Optional[int] = Field(
        default=None, sa_column=Column("refresh_token_id", Integer)
    )
    is_enable: Optional[int] = Field(
        default=None, sa_column=Column("is_enable", TINYINT(1))
    )

    oidc_authorization: Optional["OidcAuthorizations"] = Relationship(
        back_populates="oidc_tokens"
    )


class AccessTokens(OidcTokens, table=True):
    __tablename__ = "access_tokens"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id"], ["oidc_tokens.access_token_id"], name="access_tokens_ibfk_1"
        ),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    hash: Optional[str] = Field(
        default=None, sa_column=Column("hash", String(255, "utf8mb4_unicode_ci"))
    )
    type: Optional[str] = Field(
        default=None, sa_column=Column("type", String(255, "utf8mb4_unicode_ci"))
    )
    scope: Optional[str] = Field(
        default=None, sa_column=Column("scope", String(255, "utf8mb4_unicode_ci"))
    )
    issued_at: Optional[datetime] = Field(
        default=None, sa_column=Column("issued_at", TIMESTAMP)
    )
    exp: Optional[datetime] = Field(default=None, sa_column=Column("exp", TIMESTAMP))
    client_id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "client_id", String(255, "utf8mb4_unicode_ci"), comment="アプリケーションID"
        ),
    )
    user_id: Optional[str] = Field(
        default=None, sa_column=Column("user_id", String(255, "utf8mb4_unicode_ci"))
    )
    revoked: Optional[int] = Field(
        default=None, sa_column=Column("revoked", TINYINT(1))
    )


class RefreshTokens(OidcTokens, table=True):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id"], ["oidc_tokens.refresh_token_id"], name="refresh_tokens_ibfk_1"
        ),
    )

    id: Optional[int] = Field(
        default=None, sa_column=Column("id", Integer, primary_key=True)
    )
    hash: Optional[str] = Field(
        default=None, sa_column=Column("hash", String(255, "utf8mb4_unicode_ci"))
    )
    type: Optional[str] = Field(
        default=None, sa_column=Column("type", String(255, "utf8mb4_unicode_ci"))
    )
    scope: Optional[str] = Field(
        default=None, sa_column=Column("scope", String(255, "utf8mb4_unicode_ci"))
    )
    issued_at: Optional[datetime] = Field(
        default=None, sa_column=Column("issued_at", TIMESTAMP)
    )
    exp: Optional[datetime] = Field(default=None, sa_column=Column("exp", TIMESTAMP))
    client_id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            "client_id", String(255, "utf8mb4_unicode_ci"), comment="アプリケーションID"
        ),
    )
    user_id: Optional[str] = Field(
        default=None, sa_column=Column("user_id", String(255, "utf8mb4_unicode_ci"))
    )
    revoked: Optional[int] = Field(
        default=None, sa_column=Column("revoked", TINYINT(1))
    )
