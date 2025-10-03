"""
Tests for authentication API endpoints.
"""

from unittest.mock import Mock, patch

from app.core.auth import create_magic_link_token
from app.tests import APITest


class TestMagicLinkRequest(APITest):
    """Tests for POST /v1/auth/magic-link endpoint."""

    @patch("app.api.auth.send_magic_link_email")
    def test_request_magic_link_new_user(self, mock_send_email):
        """Test requesting magic link for a new user creates the user."""
        mock_send_email.return_value = None
        
        response = self.client.post(
            "/v1/auth/magic-link",
            json={"email": "newuser@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Magic link sent to your email."
        
        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]
        assert call_args[0] == "newuser@example.com"
        assert "token=" in call_args[1]

    @patch("app.api.auth.send_magic_link_email")
    def test_request_magic_link_existing_user(self, mock_send_email):
        """Test requesting magic link for existing user."""
        mock_send_email.return_value = None
        
        # Create user first
        user = self._create_user("existing@example.com")
        
        response = self.client.post(
            "/v1/auth/magic-link",
            json={"email": "existing@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Magic link sent to your email."
        
        # Verify email was sent
        mock_send_email.assert_called_once()

    def test_request_magic_link_invalid_email(self):
        """Test requesting magic link with invalid email format."""
        response = self.client.post(
            "/v1/auth/magic-link",
            json={"email": "not-an-email"}
        )

        assert response.status_code == 422  # Validation error

    @patch("app.api.auth.send_magic_link_email")
    def test_request_magic_link_email_failure(self, mock_send_email):
        """Test handling email send failure."""
        mock_send_email.side_effect = Exception("SMTP error")
        
        response = self.client.post(
            "/v1/auth/magic-link",
            json={"email": "test@example.com"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "Failed to send magic link email" in data["error"]


class TestVerifyMagicLink(APITest):
    """Tests for POST /v1/auth/verify endpoint."""

    def test_verify_valid_token(self):
        """Test verifying a valid magic link token."""
        # Create user
        user = self._create_user("test@example.com", "Test User")
        
        # Generate magic link token
        token = create_magic_link_token(user.email)
        
        response = self.client.post(
            "/v1/auth/verify",
            json={"token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "jwt" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"
        assert data["user"]["id"] == f"user_{user.id}"

    def test_verify_valid_token_user_without_name(self):
        """Test verifying token for user without full_name."""
        # Create user without full_name
        user = self._create_user("test@example.com", full_name=None)
        
        # Generate magic link token
        token = create_magic_link_token(user.email)
        
        response = self.client.post(
            "/v1/auth/verify",
            json={"token": token}
        )

        assert response.status_code == 200
        data = response.json()
        # Should default to email username
        assert data["user"]["name"] == "test"

    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        response = self.client.post(
            "/v1/auth/verify",
            json={"token": "invalid-token"}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Invalid or expired token."

    def test_verify_expired_token(self):
        """Test verifying an expired token."""
        # Create a token that's already expired (using regular JWT with short expiry)
        from datetime import timedelta
        from app.core.auth import create_access_token
        
        # Create token with -1 minute expiry (already expired)
        expired_token = create_access_token(
            {"sub": "test@example.com", "type": "magic_link"},
            expires_delta=timedelta(minutes=-1)
        )
        
        response = self.client.post(
            "/v1/auth/verify",
            json={"token": expired_token}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Invalid or expired token."

    def test_verify_token_without_user(self):
        """Test verifying token for non-existent user."""
        # Generate token for email that doesn't exist
        token = create_magic_link_token("nonexistent@example.com")
        
        response = self.client.post(
            "/v1/auth/verify",
            json={"token": token}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Invalid or expired token."

    def test_verify_regular_jwt_token(self):
        """Test that regular JWT tokens are rejected."""
        # Create user
        user = self._create_user("test@example.com")
        
        # Generate regular access token (not magic link)
        from app.core.auth import create_access_token
        regular_token = create_access_token({"sub": str(user.id)})
        
        response = self.client.post(
            "/v1/auth/verify",
            json={"token": regular_token}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Invalid or expired token."
