"""
utils.email_notification
No-op email notification helpers used during local development.
These preserve the function signatures expected by the app but do not send real emails.
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def send_announcement_email(student_email: str, announcement_title: str, announcement_message: str, faculty_name: str) -> bool:
    """No-op send single announcement email. Returns False to indicate not sent."""
    logger.info(f"[NO-OP] send_announcement_email to {student_email} (title={announcement_title})")
    return False


def send_announcement_emails_bulk(student_emails: List[str], announcement_title: str, announcement_message: str, faculty_name: str) -> Dict[str, int]:
    """No-op bulk send. Returns a result dict with zeros."""
    logger.info(f"[NO-OP] send_announcement_emails_bulk to {len(student_emails)} recipients")
    return {'sent': 0, 'failed': len(student_emails)}


def send_event_email(student_email: str, event_title: str, event_description: str, start_time, end_time, location: str, faculty_name: str) -> bool:
    logger.info(f"[NO-OP] send_event_email to {student_email} (title={event_title})")
    return False


def send_event_emails_bulk(student_emails: List[str], event_title: str, event_description: str, start_time, end_time, location: str, faculty_name: str) -> Dict[str, int]:
    logger.info(f"[NO-OP] send_event_emails_bulk to {len(student_emails)} recipients")
    return {'sent': 0, 'failed': len(student_emails)}


# Backwards-compatible class
class EmailNotificationService:
    def __init__(self):
        logger.info("[NO-OP] EmailNotificationService initialized (no Gmail integration)")

    def create_message(self, to: str, subject: str, html: str, plain_text: str = ""):
        return None

    def send_email(self, to: str, subject: str, html: str, plain_text: str = "") -> bool:
        return False

    def send_bulk_emails(self, recipients: List[str], subject: str, html: str, plain_text: str = "") -> Dict[str, int]:
        return {'sent': 0, 'failed': len(recipients)}
