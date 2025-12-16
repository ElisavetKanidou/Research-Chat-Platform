"""
Email notification service
backend/app/services/email_service.py
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from jinja2 import Template
import aiosmtplib


class EmailService:
    """Service for sending email notifications"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Research Platform")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict:
        """Send an email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add plain text version
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )

            print(f"✅ Email sent to {to_email}: {subject}")
            return {
                'success': True,
                'to': to_email,
                'subject': subject
            }

        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
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

        html_content = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #3b82f6; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9fafb; }
                .comment { background-color: white; padding: 15px; border-left: 4px solid #3b82f6; margin: 15px 0; }
                .button { display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }
                .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Comment</h1>
                </div>
                <div class="content">
                    <p>Hi """ + to_name + """,</p>
                    <p><strong>""" + author_name + """</strong> commented on your paper <strong>\"""" + paper_title + """\"</strong>:</p>
                    <div class="comment">
                        """ + comment_content + """
                    </div>
                    <a href=\"""" + paper_url + """\" class="button">View Paper</a>
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


email_service = EmailService()
