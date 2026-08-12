"""Alert Router - Routes alerts to correct channels by severity"""

from typing import Dict, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"
    NORMAL = "normal"
    URGENT = "urgent"
    CRITICAL = "critical"


class AlertRouter:
    """Routes alerts to Discord, Slack, Email, SMS based on severity"""

    def __init__(self, discord_bot, slack_bot, email_notifier, sms_notifier):
        self.discord = discord_bot
        self.slack = slack_bot
        self.email = email_notifier
        self.sms = sms_notifier

        # Routing rules
        self.routes = {
            AlertSeverity.INFO: ['discord'],
            AlertSeverity.NORMAL: ['discord'],
            AlertSeverity.URGENT: ['discord', 'slack'],
            AlertSeverity.CRITICAL: ['discord', 'slack', 'email', 'sms'],
        }

    def route_alert(self, message: str, category: str, severity: AlertSeverity, details: Dict = None):
        """Route an alert to appropriate channels"""
        channels = self.routes.get(severity, ['discord'])
        logger.info(f"Routing {severity.value} alert to {channels}: {message}")

        for channel in channels:
            try:
                if channel == 'discord':
                    self.discord.send_alert(message, category, severity.value)
                elif channel == 'slack':
                    self.slack.send_alert(message, category, severity.value)
                elif channel == 'email':
                    self.email.send_alert(message, category, severity.value)
                elif channel == 'sms':
                    self.sms.send_alert(message, severity.value)
            except Exception as e:
                logger.error(f"Error sending to {channel}: {e}")

    def route_business_alert(self, message: str, details: Dict):
        """Route business event alert"""
        self.route_alert(message, "business", AlertSeverity.NORMAL, details)

    def route_trading_alert(self, message: str, details: Dict):
        """Route trading alert"""
        self.route_alert(message, "trading", AlertSeverity.NORMAL, details)

    def route_system_alert(self, message: str, details: Dict):
        """Route system alert"""
        self.route_alert(message, "system", AlertSeverity.URGENT, details)

    def route_critical_alert(self, message: str, details: Dict):
        """Route critical alert (all channels)"""
        self.route_alert(message, "critical", AlertSeverity.CRITICAL, details)
