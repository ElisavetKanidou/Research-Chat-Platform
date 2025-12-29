"""
Email notification service using Resend API
backend/app/services/email_service.py
"""
import httpx
import logging
from typing import List, Optional, Dict, Any
from app.core.config import get_resend_config

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications via Resend"""

    def __init__(self):
        config = get_resend_config()
        self.api_key = config.get("api_key")
        self.from_email = config.get("from_email")
        self.from_name = config.get("from_name")
        self.api_url = "https://api.resend.com/emails"
        self.enabled = bool(self.api_key)

        if self.enabled:
            logger.info("✅ Resend Email Service initialized")
        else:
            logger.warning("⚠️  Resend Email Service not configured (missing API key)")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict:
        """
        Send an email via Resend API

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body
            text_content: Plain text body (optional)

        Returns:
            Response dict with success status
        """
        if not self.enabled:
            logger.error("❌ Cannot send email: Resend API key not configured")
            return {
                'success': False,
                'error': 'Email service not configured'
            }

        # Build email payload
        payload = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }

        if text_content:
            payload["text"] = text_content

        logger.info(f"📧 Sending email to {to_email} - Subject: {subject}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Email sent successfully! ID: {result.get('id')}")
                    return {
                        'success': True,
                        'to': to_email,
                        'subject': subject,
                        'id': result.get('id')
                    }
                else:
                    error_detail = response.text
                    logger.error(f"❌ Failed to send email: {error_detail}")
                    return {
                        'success': False,
                        'error': f"Resend API error: {error_detail}"
                    }

        except Exception as e:
            logger.error(f"💥 Email sending failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    async def send_comment_notification(
        self,
        to_email: str,
        to_name: str,
        author_name: str,
        paper_title: str,
        comment_content: str,
        paper_url: str
    ) -> Dict:
        """Send notification about new comment"""
        subject = f"New comment on '{paper_title}'"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .comment {{ background-color: white; padding: 15px; border-left: 4px solid #3b82f6; margin: 15px 0; border-radius: 4px; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💬 New Comment</h1>
                </div>
                <div class="content">
                    <p>Hi {to_name},</p>
                    <p><strong>{author_name}</strong> commented on your paper <strong>"{paper_title}"</strong>:</p>
                    <div class="comment">
                        {comment_content}
                    </div>
                    <a href="{paper_url}" class="button">View Paper</a>
                </div>
                <div class="footer">
                    <p>You received this email because you are a collaborator on this paper.</p>
                    <p>Research Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_welcome_email(self, user_email: str, user_name: str) -> Dict[str, Any]:
        """Send welcome email to new user"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1>Welcome to Research Platform, {user_name}! 🎉</h1>
                <p>Your account has been successfully created.</p>
                <p>You can now:</p>
                <ul>
                    <li>✍️ Create and manage research papers</li>
                    <li>🤖 Get AI-powered writing assistance</li>
                    <li>👥 Collaborate with co-authors</li>
                    <li>📊 Track your research progress</li>
                </ul>
                <p>Get started by creating your first paper!</p>
                <br>
                <p>Best regards,<br>The Research Platform Team</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=user_email,
            subject="Welcome to Research Platform! 🎉",
            html_content=html
        )

    async def send_collaboration_invite(
        self,
        to_email: str,
        inviter_name: str,
        paper_title: str,
        role: str,
        invite_url: str
    ) -> Dict[str, Any]:
        """Send collaboration invitation email"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>You've been invited to collaborate! 🤝</h2>
                <p><strong>{inviter_name}</strong> has invited you to collaborate on:</p>
                <h3>{paper_title}</h3>
                <p>Your role: <strong>{role}</strong></p>
                <br>
                <p><a href="{invite_url}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Accept Invitation</a></p>
                <br>
                <p>This invitation will expire in 7 days.</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=to_email,
            subject=f"Collaboration Invitation: {paper_title}",
            html_content=html
        )

    async def send_password_reset_email(
        self,
        user_email: str,
        reset_url: str
    ) -> Dict[str, Any]:
        """Send password reset email"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Password Reset Request 🔒</h2>
                <p>We received a request to reset your password.</p>
                <p>Click the button below to reset your password:</p>
                <br>
                <p><a href="{reset_url}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a></p>
                <br>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=user_email,
            subject="Password Reset Request",
            html_content=html
        )


# Create singleton instance
email_service = EmailService()
