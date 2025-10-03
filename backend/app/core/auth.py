"""
Authentication utilities and dependencies.
"""

from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import User
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

settings = get_settings()
security = HTTPBearer(auto_error=False)


def get_email_service() -> EmailService:
    """Get EmailService instance."""
    return EmailService(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        from_email=settings.from_email,
        smtp_user=settings.smtp_user,
        smtp_password=settings.smtp_password,
    )


def get_auth_service(
    email_service: EmailService = Depends(get_email_service),
) -> AuthService:
    """Get AuthService instance."""
    return AuthService(email_service=email_service, settings=settings)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def create_magic_link_token(email: str) -> str:
    """
    Create magic link token for email authentication.

    Args:
        email: User email address

    Returns:
        JWT token valid for 15 minutes
    """
    expires_delta = timedelta(minutes=15)
    return create_access_token(
        {"sub": email, "type": "magic_link"}, expires_delta=expires_delta
    )


def verify_magic_link_token(token: str) -> str | None:
    """
    Verify magic link token and return email.

    Args:
        token: JWT token from magic link

    Returns:
        Email address if valid, None otherwise
    """
    payload = verify_token(token)
    if not payload:
        return None

    # Check token type
    if payload.get("type") != "magic_link":
        return None

    email = payload.get("sub")
    return email if email else None


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Get current user from JWT token. Returns None if not authenticated.
    This dependency does not raise exceptions for missing/invalid tokens.
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current user from JWT token. Raises exception if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
