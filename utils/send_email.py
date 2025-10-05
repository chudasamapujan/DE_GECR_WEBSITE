"""Send email helper using SendGrid with graceful fallback to Flask-Mail or logger

This helper centralizes sending HTML/text emails. It looks for SENDGRID_API_KEY
in the environment and will use SendGrid if available. Otherwise it will fall
back to Flask-Mail if configured on the Flask app, or log the message.
"""
import os
import logging
from typing import Optional

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except Exception:
    SENDGRID_AVAILABLE = False

from flask import current_app

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_content: str = None, plain_text: str = None, from_email: Optional[str] = None):
    """Send an email via SendGrid, Flask-Mail, or log as fallback.

    Returns True on success, False otherwise.
    """
    from_email = from_email or current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@gec-rajkot.edu')

    # 1) Try SendGrid if available and API key is present
    sendgrid_key = os.environ.get('SENDGRID_API_KEY') or current_app.config.get('SENDGRID_API_KEY')
    if SENDGRID_AVAILABLE and sendgrid_key:
        try:
            sg = SendGridAPIClient(sendgrid_key)
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=plain_text or '',
                html_content=html_content or plain_text or ''
            )
            response = sg.send(message)
            logger.info(f"SendGrid response: {response.status_code}")
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")

    # 2) Fallback to Flask-Mail if configured on the app
    try:
        mail = current_app.mail if hasattr(current_app, 'mail') else None
        if mail and current_app.config.get('MAIL_USERNAME'):
            from flask_mail import Message
            msg = Message(subject=subject, sender=from_email, recipients=[to_email])
            if html_content:
                msg.html = html_content
            if plain_text:
                msg.body = plain_text
            mail.send(msg)
            return True
    except Exception as e:
        logger.error(f"Flask-Mail send failed: {e}")

    # 3) Last fallback: log the message (useful for development)
    logger.info(f"Email to {to_email} - Subject: {subject} - Plain: {plain_text} - HTML: {html_content}")
    return False
