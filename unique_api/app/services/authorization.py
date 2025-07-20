from uuid import uuid4
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from unique_api.app.model import (
    Auths,
    Code,
    OidcAuthorizations,
    Consents
)


def extract_authorized_scopes(existing_auth: Auths) -> set[str]:
    scopes = set()
    for oidc_auth in existing_auth.oidc_authorizations:
        if oidc_auth.consent and oidc_auth.consent.scope:
            scopes.update(oidc_auth.consent.scope.split())
    return scopes


def is_scope_authorized(requested_scope: str, authorized_scopes: set[str]) -> bool:
    return set(requested_scope.split()) <= authorized_scopes


def get_or_create_auth(db: Session, user_id: int, app_id: str) -> Auths:
    auth = db.query(Auths).filter_by(auth_user_id=user_id, app_id=app_id).first()
    if auth is None:
        auth = Auths(auth_user_id=user_id, app_id=app_id)
        db.add(auth)
        db.flush()  # auth.id を使いたいのでここでflush
    return auth


def create_oidc_authorization(
    db: Session, auth: Auths, scope: str
) -> OidcAuthorizations:
    consent = Consents(scope=scope, is_enable=True)
    code = Code(
        token=str(uuid4()),
        exp=datetime.now(timezone.utc) + timedelta(minutes=10),
        is_enable=True,
    )
    oidc_auth = OidcAuthorizations(
        auth_id=auth.id,
        code=code,
        consent=consent,
    )

    db.add_all([consent, code, oidc_auth])
    db.commit()
    return oidc_auth
