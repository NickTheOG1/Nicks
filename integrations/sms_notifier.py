"""SMS Notifier - Critical SMS alerts"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SMSNotifier:
    """Sends critical SMS alerts via Twilio"""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.critical_numbers = []
        logger.info("SMS Notifier initialized")

    def add_recipient(self, phone_number: str):
        """Add phone number for critical alerts"""
        self.critical_numbers.append(phone_number)
        logger.info(f"Added SMS recipient: {phone_number}")

    def send_alert(self, message: str, severity: str = "critical", recipient: Optional[str] = None):
        """Send SMS alert (critical only)"""
        if severity != "critical":
            return  # Only send critical alerts via SMS

        to_number = recipient or (self.critical_numbers[0] if self.critical_numbers else None)
        if not to_number:
            logger.warning("No SMS recipient configured")
            return

        # Limit message length
        sms_message = message[:160]
        logger.info(f"SMS sent to {to_number}: {sms_message}")
        # In production, would send via Twilio API
