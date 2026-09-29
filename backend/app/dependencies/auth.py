"""
FastAPI dependency: get_current_user

This dependency:
1. Extracts the Bearer token from the Authorization header
2. Verifies it using Supabase's JWT secret
3. Looks up our internal User record by supabase_user_id
4. Auto-creates the user on first login (first-login elevation for Super Admin)
5. Returns the authenticated User model

Usage in a route:
    @router.get("/me")
    def get_me(current_user: User = Depends(get_current_user)):
        return current_user
"""

from datetime import datetime, timezone

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError, UnauthorizedError
from app.core.security import extract_bearer_token, verify_supabase_token
from app.db.session import get_db
from app.shared.models import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate the request and return the current User.

    This is the primary authentication dependency. All protected
    routes should depend on this function.

    First-login elevation:
    If the authenticated user's email matches SUPER_ADMIN_EMAIL
    and they don't yet exist in our database, they are created
    with is_super_admin=True automatically.
    """
    # 1. Extract the token from the Authorization header
    authorization = request.headers.get("Authorization")
    token = extract_bearer_token(authorization)

    # 2. Verify the JWT using Supabase's secret
    payload = verify_supabase_token(token)

    supabase_user_id = payload.get("sub")
    email = payload.get("email", "")

    # 3. Look up or create our internal user record
    user = db.query(User).filter(User.supabase_user_id == supabase_user_id).first()

    if not user:
        # First login — auto-provision the user
        is_super_admin = (
            bool(settings.super_admin_email)
            and email.lower() == settings.super_admin_email.lower()
        )

        user = User(
            supabase_user_id=supabase_user_id,
            email=email,
            display_name=payload.get("user_metadata", {}).get("full_name", email.split("@")[0]),
            is_super_admin=is_super_admin,
            status="active",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4. Verify the user account is active
    if user.status != "active":
        raise UnauthorizedError(
            message=f"Your account has been {user.status}. Please contact support.",
            error_code="ACCOUNT_NOT_ACTIVE",
        )

    # 5. Store user in request state for logging middleware
    request.state.current_user = user

    return user


def get_current_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that requires the current user to be a Super Admin.

    Usage:
        @router.get("/super-admin/organizations")
        def list_orgs(admin: User = Depends(get_current_super_admin)):
            ...
    """
    from app.core.exceptions import SuperAdminRequiredError

    if not current_user.is_super_admin:
        raise SuperAdminRequiredError()

    return current_user
