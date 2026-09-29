"""
Security utilities for JWT verification and token handling.

Supabase issues JWTs signed with HS256 using the project's JWT_SECRET.
FastAPI verifies these tokens server-side — the frontend never needs the secret.
"""

from datetime import datetime
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError, UnauthorizedError


def verify_supabase_token(token: str) -> dict:
    """
    Verify a Supabase-issued JWT access token.
    """
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
        
        # Check if secret is configured
        secret_is_placeholder = (
            not settings.supabase_jwt_secret 
            or settings.supabase_jwt_secret == "your-jwt-secret-here"
        )

        options = {"verify_aud": False}
        if secret_is_placeholder and settings.debug:
            # In local dev with placeholder secret, decode without verifying signature
            options["verify_signature"] = False
            secret = ""
        else:
            secret = settings.supabase_jwt_secret

        payload = jwt.decode(
            token,
            secret,
            algorithms=[alg, "HS256", "RS256", "ES256"],
            options=options,
        )

        # The 'sub' claim is the Supabase user UUID
        if not payload.get("sub"):
            raise AuthenticationError("Token missing subject claim")

        return payload

    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def extract_bearer_token(authorization_header: Optional[str]) -> str:
    """
    Extract the token from an Authorization: Bearer <token> header.

    Args:
        authorization_header: The raw Authorization header value

    Returns:
        str: The raw token string

    Raises:
        AuthenticationError: If the header is missing or malformed
    """
    if not authorization_header:
        raise AuthenticationError("Authorization header is required")

    parts = authorization_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Authorization header must be 'Bearer <token>'")

    token = parts[1].strip()
    if not token:
        raise AuthenticationError("Token cannot be empty")

    return token
