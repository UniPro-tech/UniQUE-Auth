from datetime import datetime
from sqlalchemy import Boolean, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    passwd_hash: Mapped[str] = mapped_column(String)
    icon_uri: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime]
    invalid: Mapped[bool] = mapped_column(Boolean, default=False)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    auths: Mapped[list["Auth"]] = relationship(back_populates="user")
    tokens: Mapped[list["Token"]] = relationship(back_populates="user")
    profile: Mapped["Profile"] = relationship(back_populates="user")
    emails: Mapped[list["Email"]] = relationship(back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    nickname: Mapped[str] = mapped_column(String, nullable=True)
    icon_uri: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")


class Email(Base):
    __tablename__ = "emails"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="emails")


class App(Base):
    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[str] = mapped_column(String, unique=True)
    client_secret: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime]
    invalid: Mapped[bool] = mapped_column(Boolean, default=False)

    redirect_uris: Mapped[list["RedirectURI"]] = relationship(back_populates="app")
    auths: Mapped[list["Auth"]] = relationship(back_populates="app")
    tokens: Mapped[list["Token"]] = relationship(back_populates="app")


class RedirectURI(Base):
    __tablename__ = "redirect_uris"

    app_id: Mapped[int] = mapped_column(ForeignKey("apps.id"), primary_key=True)
    uri: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime]

    app: Mapped["App"] = relationship(back_populates="redirect_uris")


class Auth(Base):
    __tablename__ = "auths"

    id: Mapped[int] = mapped_column(primary_key=True)
    auth_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    app_id: Mapped[int] = mapped_column(ForeignKey("apps.id"))
    created_at: Mapped[datetime]
    invalid: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="auths")
    app: Mapped["App"] = relationship(back_populates="auths")
    oidc_authorizations: Mapped[list["OIDCAuthorization"]] = relationship(
        back_populates="auth"
    )


class OIDCAuthorization(Base):
    __tablename__ = "oidc_authorizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    auth_id: Mapped[int] = mapped_column(ForeignKey("auths.id"))
    code_id: Mapped[int] = mapped_column(ForeignKey("codes.id"))
    consent_id: Mapped[int] = mapped_column(ForeignKey("consents.id"))

    code: Mapped["Code"] = relationship(back_populates="oidc_authorization")
    consent: Mapped["Consent"] = relationship(back_populates="oidc_authorization")
    auth: Mapped["Auth"] = relationship(back_populates="oidc_authorizations")
    oidc_token: Mapped["OIDCTokens"] = relationship(back_populates="oidc_authorization")


class OIDCTokens(Base):
    __tablename__ = "oidc_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    oidc_authorization_id: Mapped[int] = mapped_column(
        ForeignKey("oidc_authorizations.id")
    )
    access_token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"))
    refresh_token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id"))
    invalid: Mapped[bool] = mapped_column(Boolean, default=False)

    access_token: Mapped["Token"] = relationship(foreign_keys=[access_token_id])
    refresh_token: Mapped["Token"] = relationship(foreign_keys=[refresh_token_id])
    oidc_authorization: Mapped["OIDCAuthorization"] = relationship(
        back_populates="oidc_token"
    )


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)  # e.g. access, refresh
    scope: Mapped[str] = mapped_column(String)
    issued_at: Mapped[datetime]
    exp: Mapped[datetime]
    client_id: Mapped[int] = mapped_column(ForeignKey("apps.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    app: Mapped["App"] = relationship(back_populates="tokens")
    user: Mapped["User"] = relationship(back_populates="tokens")


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    scope: Mapped[str] = mapped_column(String)
    invali: Mapped[bool] = mapped_column(Boolean)

    oidc_authorization: Mapped["OIDCAuthorization"] = relationship(
        back_populates="consent"
    )


class Code(Base):
    __tablename__ = "codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    exp: Mapped[datetime] = mapped_column(DateTime)
    invalid: Mapped[bool] = mapped_column(Boolean, default=False)

    oidc_authorization: Mapped["OIDCAuthorization"] = relationship(
        back_populates="code"
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ip_address: Mapped[str] = mapped_column(String)
    user_agent: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime]
    invalid: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="sessions")
