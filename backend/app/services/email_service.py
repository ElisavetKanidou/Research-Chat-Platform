
"""
Email Service (app/services/email_service.py) - Enhanced version
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class EmailService:
    """Enhanced email service"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME

        # Email templates
        self.templates = {
            "welcome": self._get_welcome_template(),
            "invitation": self._get_invitation_template(),
            "password_reset": self._get_password_reset_template(),
            "paper_shared": self._get_paper_shared_template()
        }

    async def send_templated_email(
            self,
            template: str,
            to_emails: List[str],
            subject: str,
            context: Dict[str, Any],
            attachments: Optional[List[str]] = None
    ) -> bool:
        """Send templated email"""

        if template not in self.templates:
            raise ValidationException(f"Unknown email template: {template}")

        # Render template
        html_body = self.templates[template].format(**context)
        text_body = self._html_to_text(html_body)

        return await self.send_email(
            to_emails=to_emails,
            subject=subject,
            body=text_body,
            html_body=html_body,
            attachments=attachments
        )

    async def send_email(
            self,
            to_emails: List[str],
            subject: str,
            body: str,
            html_body: Optional[str] = None,
            attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email with optional attachments"""

        if not self.smtp_host:
            logger.warning("SMTP not configured, email not sent")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to_emails)

            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {Path(file_path).name}',
                        )
                        msg.attach(part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(msg)

            logger.info(f"Email sent to {len(to_emails)} recipients")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def _get_welcome_template(self) -> str:
        """Welcome email template"""
        return """
        <html>
        <body>
            <h2>Welcome to Research Platform, {user_name}!</h2>
            <p>We're excited to help you with your research journey.</p>

            <h3>Get started by:</h3>
            <ul>
                <li>Creating your first research paper</li>
                <li>Exploring AI-powered research assistance</li>
                <li>Setting up your research preferences</li>
            </ul>

            <p>If you have any questions, don't hesitate to reach out.</p>
            <p>Best regards,<br>The Research Platform Team</p>
        </body>
        </html>
        """

    def _get_invitation_template(self) -> str:
        """Collaboration invitation template"""
        return """
        <html>
        <body>
            <h2>Collaboration Invitation</h2>
            <p>You've been invited to collaborate on the research paper "{paper_title}".</p>

            <p><strong>Role:</strong> {role}</p>
            <p><strong>Invited by:</strong> {inviter_name}</p>

            {message}

            <p><a href="{accept_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accept Invitation</a></p>

            <p><small>This invitation expires on {expiry_date}.</small></p>
        </body>
        </html>
        """

    def _get_password_reset_template(self) -> str:
        """Password reset template"""
        return """
        <html>
        <body>
            <h2>Reset Your Password</h2>
            <p>You requested a password reset for your Research Platform account.</p>

            <p><a href="{reset_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>

            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """

    def _get_paper_shared_template(self) -> str:
        """Paper shared template"""
        return """
        <html>
        <body>
            <h2>Paper Shared With You</h2>
            <p>{sharer_name} has shared the research paper "{paper_title}" with you.</p>

            <p><strong>Research Area:</strong> {research_area}</p>
            <p><strong>Status:</strong> {status}</p>

            <p><a href="{paper_url}" style="background-color: #17a2b8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Paper</a></p>
        </body>
        </html>
        """

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text"""
        # Simple HTML to text conversion
        import re
        text = re.sub('<[^<]+?>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


# Create service instance
email_service = EmailService()