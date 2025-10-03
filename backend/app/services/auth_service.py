"""
AuthService: Encapsulates authentication business logic.
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import Settings
from app.services.email_service import EmailService


class AuthService:
    """Service for authentication operations."""

    def __init__(self, email_service: EmailService, settings: Settings):
        """
        Initialize AuthService.
        
        Args:
            email_service: Email service for sending magic links
            settings: Application settings
        """
        self.email_service = email_service
        self.settings = settings

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.settings.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> dict | None:
        """
        Verify JWT token and return payload.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm],
            )
            return payload
        except JWTError:
            return None

    def create_magic_link_token(self, email: str) -> str:
        """
        Create magic link token for email authentication.
        
        Args:
            email: User email address
            
        Returns:
            JWT token valid for 15 minutes
        """
        expires_delta = timedelta(minutes=15)
        return self.create_access_token(
            {"sub": email, "type": "magic_link"}, expires_delta=expires_delta
        )

    def verify_magic_link_token(self, token: str) -> str | None:
        """
        Verify magic link token and return email.
        
        Args:
            token: JWT token from magic link
            
        Returns:
            Email address if valid, None otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return None

        # Check token type
        if payload.get("type") != "magic_link":
            return None

        email = payload.get("sub")
        return email if email else None

    def send_magic_link(self, email: str, frontend_url: str) -> None:
        """
        Generate and send magic link to user's email.
        
        Args:
            email: User email address
            frontend_url: Frontend base URL for constructing magic link
        """
        token = self.create_magic_link_token(email)
        magic_link = f"{frontend_url}/auth/verify?token={token}"
        self.email_service.send_magic_link_email(email, magic_link)
