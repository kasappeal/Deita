"""
UserService: Encapsulates business logic for user operations.
"""

from sqlalchemy.orm import Session

from app.models import User


class UserService:
    """Service for user-related operations."""

    def __init__(self, db: Session):
        """
        Initialize UserService.
        
        Args:
            db: Database session
        """
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email address.
        
        Args:
            email: User email address (case-insensitive)
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email.lower()).first()

    def create_user(self, email: str, full_name: str | None = None) -> User:
        """
        Create a new user.
        
        Args:
            email: User email address
            full_name: User's full name (optional)
            
        Returns:
            Created user object
        """
        user = User(email=email.lower(), full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_or_create_user(self, email: str, full_name: str | None = None) -> User:
        """
        Get existing user by email or create new one if not exists.
        
        Args:
            email: User email address
            full_name: User's full name (optional, only used if creating new user)
            
        Returns:
            User object (existing or newly created)
        """
        user = self.get_user_by_email(email)
        if not user:
            user = self.create_user(email, full_name)
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
