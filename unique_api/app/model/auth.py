from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from unique_api.app.db import Base
from unique_api.app.model.util import generate_ulid
if TYPE_CHECKING:
    from unique_api.app.model.user import Users
    from unique_api.app.model.app import Apps


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
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    app: Mapped["Apps"] = relationship("Apps", back_populates="auths")
    auth_user: Mapped["Users"] = relationship("Users", back_populates="auths")
    oidc_authorizations: Mapped[List["OidcAuthorizations"]] = relationship(
        "OidcAuthorizations", back_populates="auth"
    )


class Code(Base):
    __tablename__ = "code"
    __table_args__ = (Index("token", "token", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    nonce: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=True)
    acr: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=True)
    amr: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=True)  # JSONでもよい
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    exp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

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
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    auth: Mapped["Auths"] = relationship("Auths", back_populates="oidc_authorizations")
    code: Mapped["Code"] = relationship("Code", back_populates="oidc_authorizations")
    consent: Mapped["Consents"] = relationship(
        "Consents", back_populates="oidc_authorizations"
    )
    token_sets: Mapped[List["TokenSets"]] = relationship(
        "TokenSets", back_populates="oidc_authorization"
    )


class TokenSets(Base):
    __tablename__ = "token_sets"
    __table_args__ = (
        ForeignKeyConstraint(
            ["oidc_authorization_id"],
            ["oidc_authorizations.id"],
            name="token_sets_ibfk_1",
        ),
        Index("oidc_authorization_id", "oidc_authorization_id", unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    oidc_authorization_id: Mapped[int] = mapped_column(Integer)
    access_token_id: Mapped[int] = mapped_column(ForeignKey("access_tokens.id"))
    refresh_token_id: Mapped[int] = mapped_column(ForeignKey("refresh_tokens.id"))
    id_token_id: Mapped[int] = mapped_column(ForeignKey("id_tokens.id"))
    is_enable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))

    oidc_authorization: Mapped["OidcAuthorizations"] = relationship(
        "OidcAuthorizations", back_populates="token_sets"
    )
    access_token: Mapped["AccessTokens"] = relationship(
        back_populates="token_set"
    )
    refresh_token: Mapped["RefreshTokens"] = relationship(
        back_populates="token_set"
    )
    id_token: Mapped["IDTokens"] = relationship(
        back_populates="token_set"
    )


class AccessTokens(Base):
    __tablename__ = "access_tokens"

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    hash: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    type: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    scope: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    issued_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    exp: Mapped[datetime] = mapped_column(TIMESTAMP)
    client_id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), comment="アプリケーションID"
    )
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    revoked: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))

    token_set: Mapped["TokenSets"] = relationship(
        back_populates="access_token"
    )


class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    hash: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    type: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    issued_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    exp: Mapped[datetime] = mapped_column(TIMESTAMP)
    client_id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), comment="アプリケーションID"
    )
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    revoked: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))

    token_set: Mapped["TokenSets"] = relationship(
        back_populates="refresh_token"
    )


class IDTokens(Base):
    __tablename__ = "id_tokens"

    id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), primary_key=True, default=generate_ulid
    )
    hash: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    type: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    issued_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    exp: Mapped[datetime] = mapped_column(TIMESTAMP)
    client_id: Mapped[str] = mapped_column(
        String(255, "utf8mb4_unicode_ci"), comment="アプリケーションID"
    )
    user_id: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    aud: Mapped[str] = mapped_column(String(255, "utf8mb4_unicode_ci"))
    nonce: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=True)
    auth_time: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    acr: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=True)
    amr: Mapped[Optional[str]] = mapped_column(String(255, "utf8mb4_unicode_ci"), nullable=True)  # JSONでもよい
    revoked: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))

    token_set: Mapped["TokenSets"] = relationship(
        back_populates="id_token"
    )
