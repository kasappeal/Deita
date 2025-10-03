"""
Authentication API routes for magic link authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, create_magic_link_token, verify_magic_link_token
from app.core.config import get_settings
from app.core.database import get_db
from app.models import User
from app.schemas import AuthResponse, MagicLinkRequest, MagicLinkResponse, VerifyTokenRequest
from app.services.email_service import send_magic_link_email

router = APIRouter()
settings = get_settings()


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """
    Request a magic link for email authentication.
    
    If the user doesn't exist, they will be created automatically.
    Sends an email with a magic link token valid for 15 minutes.
    """
    email = request.email.lower()
    
    # Check if user exists, create if not
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate magic link token
    token = create_magic_link_token(email)
    
    # In production, this would be the frontend URL
    # For now, we'll use a placeholder that can be configured
    frontend_url = settings.allowed_origins[0] if settings.allowed_origins else "http://localhost:3000"
    magic_link = f"{frontend_url}/auth/verify?token={token}"
    
    # Send email with magic link
    try:
        send_magic_link_email(email, magic_link)
    except Exception as e:
        # Log error but don't expose details to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send magic link email. Please try again later."
        )
    
    return MagicLinkResponse(message="Magic link sent to your email.")


@router.post("/verify", response_model=AuthResponse)
async def verify_magic_link(
    request: VerifyTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Verify magic link token and issue JWT access token.
    
    Returns a JWT token and user information if the magic link token is valid.
    """
    # Verify the magic link token
    email = verify_magic_link_token(request.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token."
        )
    
    # Get user from database
    user = db.query(User).filter(User.email == email.lower()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token."
        )
    
    # Create JWT access token
    access_token = create_access_token({"sub": str(user.id)})
    
    # Return JWT and user info
    return AuthResponse(
        jwt=access_token,
        user={
            "id": f"user_{user.id}",
            "email": user.email,
            "name": user.full_name or user.email.split("@")[0]
        }
    )
