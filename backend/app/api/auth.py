"""
Authentication API routes for magic link authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_auth_service
from app.core.config import get_settings
from app.core.database import get_db
from app.schemas import AuthResponse, MagicLinkRequest, MagicLinkResponse, VerifyTokenRequest
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()
settings = get_settings()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get UserService instance."""
    return UserService(db=db)


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Request a magic link for email authentication.

    If the user doesn't exist, they will be created automatically.
    Sends an email with a magic link token valid for 15 minutes.
    """
    email = request.email.lower()

    # Check if user exists, create if not
    user = user_service.get_or_create_user(email)

    # Send email with magic link
    try:
        auth_service.send_magic_link(email, settings.frontend_url)
    except Exception as e:
        # Log error but don't expose details to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send magic link email. Please try again later.",
        )

    return MagicLinkResponse(message="Magic link sent to your email.")


@router.post("/verify", response_model=AuthResponse)
async def verify_magic_link(
    request: VerifyTokenRequest,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Verify magic link token and issue JWT access token.

    Returns a JWT token and user information if the magic link token is valid.
    """
    # Verify the magic link token
    email = auth_service.verify_magic_link_token(request.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token.",
        )

    # Get user from database
    user = user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token.",
        )

    # Create JWT access token
    access_token = auth_service.create_access_token({"sub": str(user.id)})

    # Return JWT and user info
    return AuthResponse(
        jwt=access_token,
        user={
            "id": f"user_{user.id}",
            "email": user.email,
            "name": user.full_name or user.email.split("@")[0],
        },
    )
