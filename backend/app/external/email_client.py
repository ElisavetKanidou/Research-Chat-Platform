
"""
Email Client (app/external/email_client.py)
"""
import httpx
from typing import List, Dict, Any, Optional
import logging

from app.core.config import settings
from app.core.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)


class EmailClient:
    """External email service client (SendGrid/Mailgun compatible)"""

    def __init__(self):
        self.api_key = getattr(settings, 'EMAIL_API_KEY', None)
        self.service = getattr(settings, 'EMAIL_SERVICE', 'sendgrid')  # sendgrid or mailgun
        self.enabled = bool(self.api_key)

        if self.service == 'sendgrid':
            self.base_url = "https://api.sendgrid.com/v3"
        elif self.service == 'mailgun':
            self.base_url = f"https://api.mailgun.net/v3/{getattr(settings, 'MAILGUN_DOMAIN', '')}"

        if not self.enabled:
            logger.warning("Email service not configured")

    async def send_email(
            self,
            to_emails: List[str],
            subject: str,
            content: str,
            html_content: Optional[str] = None,
            template_id: Optional[str] = None,
            template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send email via external service"""

        if not self.enabled:
            return False

        try:
            if self.service == 'sendgrid':
                return await self._send_via_sendgrid(
                    to_emails, subject, content, html_content, template_id, template_data
                )
            elif self.service == 'mailgun':
                return await self._send_via_mailgun(
                    to_emails, subject, content, html_content
                )

            return False

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    async def _send_via_sendgrid(
            self,
            to_emails: List[str],
            subject: str,
            content: str,
            html_content: Optional[str] = None,
            template_id: Optional[str] = None,
            template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send email via SendGrid"""

        async with httpx.AsyncClient() as client:
            payload = {
                "personalizations": [
                    {
                        "to": [{"email": email} for email in to_emails],
                        "dynamic_template_data": template_data or {}
                    }
                ],
                "from": {"email": settings.EMAIL_FROM, "name": settings.EMAIL_FROM_NAME},
                "subject": subject
            }

            if template_id:
                payload["template_id"] = template_id
            else:
                payload["content"] = [{"type": "text/plain", "value": content}]
                if html_content:
                    payload["content"].append({"type": "text/html", "value": html_content})

            response = await client.post(
                f"{self.base_url}/mail/send",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )

            return response.status_code == 202

    async def _send_via_mailgun(
            self,
            to_emails: List[str],
            subject: str,
            content: str,
            html_content: Optional[str] = None
    ) -> bool:
        """Send email via Mailgun"""

        async with httpx.AsyncClient() as client:
            data = {
                "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
                "to": to_emails,
                "subject": subject,
                "text": content
            }

            if html_content:
                data["html"] = html_content

            response = await client.post(
                f"{self.base_url}/messages",
                data=data,
                auth=("api", self.api_key)
            )

            return response.status_code == 200


# Create client instance
email_client = EmailClient()
