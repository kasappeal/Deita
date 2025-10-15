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
            raise Exception(f"Failed to send email: {str(e)}") from e

    def send_workspace_deletion_warning(
        self,
        to_email: str,
        workspace_name: str,
        workspace_id: str,
        days_until_deletion: int,
        deletion_date: str,
        file_count: int,
        storage_used_mb: float,
        workspace_url: str,
    ) -> None:
        """
        Send workspace deletion warning email to owner.

        Args:
            to_email: Recipient email address
            workspace_name: Name of the workspace
            workspace_id: ID of the workspace
            days_until_deletion: Number of days until deletion
            deletion_date: Formatted deletion date string
            file_count: Number of files in workspace
            storage_used_mb: Storage used in MB
            workspace_url: URL to access workspace
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⚠️ Workspace '{workspace_name}' will be deleted in {days_until_deletion} day{'s' if days_until_deletion != 1 else ''}"
        msg["From"] = self.from_email
        msg["To"] = to_email

        # Create plain text version
        text = f"""
Hi,

This is a reminder that your Deita workspace will be deleted soon due to inactivity.

Workspace Details:
- Name: {workspace_name}
- ID: {workspace_id}
- Files: {file_count}
- Storage Used: {storage_used_mb:.2f} MB
- Days Until Deletion: {days_until_deletion}
- Scheduled Deletion: {deletion_date}

To keep your workspace, simply access it before the deletion date:
{workspace_url}

Accessing your workspace will reset the inactivity timer and cancel the scheduled deletion.

If you don't need this workspace anymore, no action is required.

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
    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px;">
        <h2 style="color: #856404; margin: 0;">⚠️ Workspace Deletion Warning</h2>
    </div>

    <p>This is a reminder that your Deita workspace will be deleted soon due to inactivity.</p>

    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #2c3e50;">Workspace Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #666;">Name:</td>
                <td style="padding: 8px 0; font-weight: bold;">{workspace_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">ID:</td>
                <td style="padding: 8px 0; font-family: monospace; font-size: 12px;">{workspace_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">Files:</td>
                <td style="padding: 8px 0;">{file_count}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">Storage Used:</td>
                <td style="padding: 8px 0;">{storage_used_mb:.2f} MB</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">Days Until Deletion:</td>
                <td style="padding: 8px 0; font-weight: bold; color: #dc3545;">{days_until_deletion}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">Scheduled Deletion:</td>
                <td style="padding: 8px 0; font-weight: bold;">{deletion_date}</td>
            </tr>
        </table>
    </div>

    <div style="text-align: center; margin: 30px 0;">
        <a href="{workspace_url}" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Keep My Workspace</a>
    </div>

    <p style="color: #666; font-size: 14px;">Accessing your workspace will reset the inactivity timer and cancel the scheduled deletion.</p>
    <p style="color: #666; font-size: 14px;">If you don't need this workspace anymore, no action is required.</p>

    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
    <p style="color: #999; font-size: 12px;">This is an automated notification from Deita.</p>
</body>
</html>
"""

        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email (no retry, fail silently as per requirements)
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception:
            # Fail silently as per requirements (no retry, no logging)
            pass

    def send_workspace_deleted_notification(
        self,
        to_email: str,
        workspace_name: str,
        workspace_id: str,
        file_count: int,
        storage_used_mb: float,
    ) -> None:
        """
        Send workspace deletion confirmation email to owner.

        Args:
            to_email: Recipient email address
            workspace_name: Name of the workspace
            workspace_id: ID of the workspace
            file_count: Number of files that were deleted
            storage_used_mb: Storage that was freed in MB
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Workspace '{workspace_name}' has been deleted"
        msg["From"] = self.from_email
        msg["To"] = to_email

        # Create plain text version
        text = f"""
Hi,

Your Deita workspace has been deleted due to inactivity.

Workspace Details:
- Name: {workspace_name}
- ID: {workspace_id}
- Files Deleted: {file_count}
- Storage Freed: {storage_used_mb:.2f} MB

The workspace and all its files have been permanently removed from our system.

If you need to continue working with data, you can create a new workspace at any time.

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
    <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin-bottom: 20px;">
        <h2 style="color: #721c24; margin: 0;">Workspace Deleted</h2>
    </div>

    <p>Your Deita workspace has been deleted due to inactivity.</p>

    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #2c3e50;">Workspace Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #666;">Name:</td>
                <td style="padding: 8px 0; font-weight: bold;">{workspace_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">ID:</td>
                <td style="padding: 8px 0; font-family: monospace; font-size: 12px;">{workspace_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">Files Deleted:</td>
                <td style="padding: 8px 0;">{file_count}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #666;">Storage Freed:</td>
                <td style="padding: 8px 0;">{storage_used_mb:.2f} MB</td>
            </tr>
        </table>
    </div>

    <p style="color: #666;">The workspace and all its files have been permanently removed from our system.</p>
    <p style="color: #666;">If you need to continue working with data, you can create a new workspace at any time.</p>

    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
    <p style="color: #999; font-size: 12px;">This is an automated notification from Deita.</p>
</body>
</html>
"""

        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email (no retry, fail silently as per requirements)
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception:
            # Fail silently as per requirements (no retry, no logging)
            pass
