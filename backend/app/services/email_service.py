"""
Email service for sending emails via SMTP.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        from_email: str,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
    ):
        """
        Initialize EmailService with SMTP settings.
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            from_email: Default sender email address
            smtp_user: SMTP username (optional)
            smtp_password: SMTP password (optional)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def send_magic_link_email(self, to_email: str, magic_link: str) -> None:
        """
        Send magic link email to user.
        
        Args:
            to_email: Recipient email address
            magic_link: Magic link URL for authentication
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your Deita Magic Link"
        msg["From"] = self.from_email
        msg["To"] = to_email

        # Create plain text version
        text = f"""
Hi,

Click the link below to sign in to Deita:

{magic_link}

This link will expire in 15 minutes.

If you didn't request this link, you can safely ignore this email.

Best regards,
The Deita Team
"""

        # Create HTML version
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #2c3e50;">Welcome to Deita</h2>
    <p>Click the button below to sign in to your account:</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="{magic_link}" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Sign In to Deita</a>
    </div>
    <p style="color: #666; font-size: 14px;">Or copy and paste this link into your browser:</p>
    <p style="word-break: break-all; color: #3498db; font-size: 14px;">{magic_link}</p>
    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
    <p style="color: #999; font-size: 12px;">This link will expire in 15 minutes.</p>
    <p style="color: #999; font-size: 12px;">If you didn't request this link, you can safely ignore this email.</p>
</body>
</html>
"""

        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                # Only use authentication if credentials are provided
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                
                server.send_message(msg)
        except Exception as e:
            # Log the error in production, for now just raise
            raise Exception(f"Failed to send email: {str(e)}")
