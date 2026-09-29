"""
Auth module router — user profile and token verification endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.shared.models import User
from app.shared.schemas import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserProfileResponse:
    pass


from pydantic import BaseModel, ConfigDict
from uuid import UUID


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str | None
    is_super_admin: bool
    status: str


@router.get(
    "/me",
    response_model=APIResponse[MeResponse],
    summary="Get current user profile",
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the authenticated user's profile.

    This endpoint is used by the frontend to:
    1. Verify the JWT is valid
    2. Get the user's profile information
    3. Determine if the user is a Super Admin

    **Requires:** Valid Supabase JWT
    """
    return APIResponse(
        success=True,
        data=MeResponse.model_validate(current_user),
    )
