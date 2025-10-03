# Magic Link Authentication - Implementation Guide

This document describes the magic link authentication implementation for Deita.

## Overview

Magic link authentication allows users to sign in via email without passwords. Users receive a link via email that, when clicked, authenticates them and provides a JWT token for accessing protected resources.

## Endpoints

### 1. Request Magic Link

**Endpoint:** `POST /v1/auth/magic-link`

**Description:** Request a magic link for email authentication. If the user doesn't exist, they will be created automatically.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "Magic link sent to your email."
}
```

**Error Responses:**
- `400 Bad Request` - Invalid email format
- `500 Internal Server Error` - Email service failure

**Example:**
```bash
curl -X POST http://localhost:8000/v1/auth/magic-link \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### 2. Verify Magic Link Token

**Endpoint:** `POST /v1/auth/verify`

**Description:** Verify magic link token and issue a JWT access token.

**Request Body:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200):**
```json
{
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "Jane Doe"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid or expired token

**Example:**
```bash
curl -X POST http://localhost:8000/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

## Implementation Details

### Token Security

- **Magic Link Token:** JWT token valid for 15 minutes
  - Contains user email in `sub` claim
  - Has `type: "magic_link"` to distinguish from access tokens
  - Signed with application secret key

- **Access Token (JWT):** Long-lived token valid for 30 days (configurable)
  - Contains user ID in `sub` claim
  - Used to authenticate API requests
  - Signed with application secret key

### Email Service

The implementation uses SMTP to send magic link emails with:
- HTML and plain text versions
- Configurable SMTP settings via environment variables
- Professional email template with clickable button and fallback link

**Required Environment Variables:**
```bash
SMTP_HOST=mailhog          # SMTP server hostname
SMTP_PORT=1025             # SMTP server port
SMTP_USER=                 # SMTP username (optional)
SMTP_PASSWORD=             # SMTP password (optional)
FROM_EMAIL=noreply@deita.app
```

### User Creation

When a user requests a magic link for the first time:
1. System checks if user exists by email
2. If not, creates new user with email
3. User's `full_name` is initially `None`
4. Can be updated later via profile endpoint (future feature)

### Database

Uses existing `users` table with fields:
- `id` (integer, primary key)
- `email` (string, unique, indexed)
- `full_name` (string, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## Testing

Run the authentication tests:
```bash
cd backend
python3 -m pytest app/tests/test_auth_endpoints.py -v
```

All 10 tests should pass:
- 4 tests for magic link request endpoint
- 6 tests for verify token endpoint

## Integration with Frontend

The frontend should:

1. **Request Magic Link:**
   - User enters email in login form
   - POST to `/v1/auth/magic-link`
   - Show success message

2. **Verify Token:**
   - User clicks magic link in email (format: `{frontend_url}/auth/verify?token={token}`)
   - Frontend extracts token from URL
   - POST to `/v1/auth/verify` with token
   - Store received JWT in localStorage/sessionStorage
   - Redirect to dashboard

3. **Use JWT for API Calls:**
   - Include JWT in Authorization header: `Bearer {jwt}`
   - JWT is automatically validated by backend

## Error Handling

All errors follow consistent format:
```json
{
  "error": "Error message here"
}
```

Common error scenarios:
- Invalid email format (422 validation error)
- Email service failure (500)
- Invalid/expired token (400)
- Missing/malformed request (422)

## Security Considerations

1. **Token Expiry:** Magic link tokens expire after 15 minutes
2. **Token Type Validation:** Regular JWT tokens are rejected in verify endpoint
3. **Email Validation:** Pydantic EmailStr ensures valid email format
4. **No Password:** No passwords stored, reducing security risk
5. **Rate Limiting:** Should be added in production (future enhancement)

## Configuration

See `backend/.env.example` for all configurable options:
- SMTP settings
- JWT secret key and expiry
- Frontend URL for magic links
- CORS origins

## Future Enhancements

Potential improvements for production:
- Rate limiting on magic link requests
- Email template customization
- Multi-language email support
- Magic link usage tracking
- Account email verification status
