"""
Tests for authentication API endpoints.
"""

from datetime import timedelta
from unittest.mock import patch

from app.core.auth import create_access_token, create_magic_link_token
from app.tests import APITest


class TestMagicLinkRequest(APITest):
    """Tests for POST /v1/auth/magic-link endpoint."""

    @patch("app.services.auth_service.AuthService.send_magic_link")
    def test_request_magic_link_new_user(self, mock_send_magic_link):
        """Test requesting magic link for a new user creates the user."""
        email = "newuser@example.com"

        response = self.client.post(
            "/v1/auth/magic-link", json={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Magic link sent to your email."
        mock_send_magic_link.assert_called_once_with(email, "http://localhost:3000")

    @patch("app.services.auth_service.AuthService.send_magic_link")
    def test_request_magic_link_existing_user(self, mock_send_magic_link):
        """Test requesting magic link for existing user."""
        email = "existing@example.com"

        # Create user first
        self._create_user(email)

        response = self.client.post(
            "/v1/auth/magic-link", json={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Magic link sent to your email."
        mock_send_magic_link.assert_called_once_with(email, "http://localhost:3000")

    def test_request_magic_link_invalid_email(self):
        """Test requesting magic link with invalid email format."""
        response = self.client.post(
            "/v1/auth/magic-link", json={"email": "not-an-email"}
        )

        assert response.status_code == 422  # Validation error

    def test_request_magic_link_email_failure(self):
        """Test handling email send failure."""
        email = "test@example.com"
        with patch("app.services.auth_service.AuthService.send_magic_link") as mock_send_magic_link:
            mock_send_magic_link.side_effect = Exception("SMTP error")

            response = self.client.post(
                "/v1/auth/magic-link", json={"email": email}
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
        """Test verifying valid token for user without full name."""
        # Create user without full name directly
        from app.models.user import User
        user = User(email="test@example.com", full_name=None)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create magic link token
        token = create_magic_link_token(user.email)

        response = self.client.post(
            "/v1/auth/verify",
            json={"token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["id"] == f"user_{user.id}"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "test"  # Should use email prefix

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
        regular_token = create_access_token({"sub": str(user.id)})

        response = self.client.post(
            "/v1/auth/verify",
            json={"token": regular_token}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "Invalid or expired token."


class TestGetCurrentUser(APITest):
    """Tests for GET /v1/auth/me endpoint."""

    def test_get_current_user_authenticated(self):
        """Test getting current user info when authenticated."""
        # Create a user
        user = self._create_user("test@example.com", "Test User")

        # Get auth headers
        headers = self._get_auth_headers(user)

        # Make request to /me endpoint
        response = self.client.get("/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == f"user_{user.id}"
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    def test_get_current_user_authenticated_no_full_name(self):
        """Test getting current user info when authenticated with no full name."""
        # Create a user without full name directly
        from app.models.user import User
        user = User(email="test2@example.com", full_name=None)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Get auth headers
        headers = self._get_auth_headers(user)

        # Make request to /me endpoint
        response = self.client.get("/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == f"user_{user.id}"
        assert data["email"] == "test2@example.com"
        assert data["name"] == "test2"  # Should use email prefix

    def test_get_current_user_unauthenticated(self):
        """Test getting current user info when not authenticated."""
        # Make request without auth headers
        response = self.client.get("/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "Not authenticated"

    def test_get_current_user_invalid_token(self):
        """Test getting current user info with invalid token."""
        # Make request with invalid auth header
        headers = {"Authorization": "Bearer invalid_token"}

        response = self.client.get("/v1/auth/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "Could not validate credentials"
