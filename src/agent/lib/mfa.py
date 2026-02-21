"""MFA placeholder for approval actions. Integrate with your IdP (Okta, Auth0)."""
import os


def require_mfa_for_approval() -> bool:
    """Whether MFA is required for approval actions."""
    return os.getenv("MFA_REQUIRED_FOR_APPROVAL", "").lower() in ("1", "true", "yes")


def verify_mfa_token(user: str, token: str) -> bool:
    """
    Stub: Verify TOTP token. Replace with real IdP integration.
    Returns True if valid.
    """
    if not require_mfa_for_approval():
        return True
    # Placeholder: would call IdP API
    return len(token) >= 6
