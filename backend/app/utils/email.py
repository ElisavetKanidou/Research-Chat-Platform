
"""
Email Utils (app/utils/email.py) - Enhanced version
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailHelper:
    """Email utility functions"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
        self.enabled = bool(self.smtp_host and self.smtp_user)

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def format_email_template(self, template: str, **kwargs) -> str:
        """Format email template with variables"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return template

    async def send_async_email(
            self,
            to_emails: List[str],
            subject: str,
            body: str,
            html_body: Optional[str] = None,
            attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email asynchronously"""

        if not self.enabled:
            logger.warning("Email not configured, skipping send")
            return False

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self._send_sync_email,
                to_emails, subject, body, html_body, attachments
            )
        except Exception as e:
            logger.error(f"Failed to send async email: {e}")
            return False

    def _send_sync_email(
            self,
            to_emails: List[str],
            subject: str,
            body: str,
            html_body: Optional[str] = None,
            attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email synchronously"""

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to_emails)

            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Add HTML part
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

            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def get_email_templates(self) -> Dict[str, str]:
        """Get predefined email templates"""
        return {
            "welcome": """
Welcome to Research Platform, {user_name}!

We're excited to help you with your research journey.

Get started by:
- Creating your first research paper
- Exploring AI-powered research assistance
- Setting up your research preferences

Best regards,
The Research Platform Team
            """,

            "paper_shared": """
Hi {recipient_name},

{sender_name} has shared a research paper with you: "{paper_title}"

Research Area: {research_area}
Status: {status}

You can view it here: {paper_url}

Best regards,
Research Platform
            """,

            "collaboration_invite": """
Hi {recipient_name},

You've been invited to collaborate on "{paper_title}" by {inviter_name}.

Role: {role}
Message: {message}

Accept invitation: {accept_url}

This invitation expires on {expiry_date}.
            """
        }

