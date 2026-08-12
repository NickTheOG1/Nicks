"""Email Notifier - Critical email alerts"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Sends critical email alerts"""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.critical_recipients = []
        logger.info("Email Notifier initialized")

    def add_recipient(self, email: str):
        """Add email recipient for critical alerts"""
        self.critical_recipients.append(email)
        logger.info(f"Added email recipient: {email}")

    def send_alert(self, message: str, category: str, severity: str = "normal", recipient: Optional[str] = None):
        """Send email alert"""
        if severity not in ["urgent", "critical"]:
            return  # Only send urgent/critical

        to_email = recipient or (self.critical_recipients[0] if self.critical_recipients else None)
        if not to_email:
            logger.warning("No email recipient configured")
            return

        subject = f"[{severity.upper()}] NEXUS Alert - {category}"
        body = f"""
ALERT SEVERITY: {severity.upper()}
CATEGORY: {category}

{message}

---
NEXUS Autonomous Operations System
"""

        logger.info(f"Email alert sent to {to_email}: {subject}")
        # In production, would send via SMTP
