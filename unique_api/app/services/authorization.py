from unique_api.app.model import (
    Auths,
)


def extract_authorized_scopes(existing_auth: Auths) -> set[str]:
    scopes = set()
    for oidc_auth in existing_auth.oidc_authorizations:
        if oidc_auth.consent and oidc_auth.consent.scope:
            scopes.update(oidc_auth.consent.scope.split())
    return scopes


def is_scope_authorized(requested_scope: str, authorized_scopes: set[str]) -> bool:
    return set(requested_scope.split()) <= authorized_scopes
