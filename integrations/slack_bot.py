"""Slack Bot - Operations command center"""

import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SlackBot:
    """NEXUS Slack Bot for operations"""

    def __init__(self, token: str, operations_channel: str = "#operations",
                 trading_channel: str = "#trading", system_channel: str = "#system"):
        self.token = token
        self.operations_channel = operations_channel
        self.trading_channel = trading_channel
        self.system_channel = system_channel
        self.connected = False
        logger.info("Slack Bot initialized")

    def connect(self) -> bool:
        """Connect to Slack"""
        try:
            logger.info("Connecting to Slack...")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Slack connection failed: {e}")
            return False

    def send_alert(self, message: str, category: str, severity: str = "normal"):
        """Send alert to Slack"""
        if not self.connected:
            logger.warning("Slack not connected")
            return

        channel = self.operations_channel
        if category == "trading":
            channel = self.trading_channel
        elif category == "system":
            channel = self.system_channel

        color = self._get_severity_color(severity)
        logger.info(f"Slack -> {channel}: {message} (color: {color})")

    def send_command_response(self, user: str, response: str):
        """Send command response"""
        logger.info(f"Slack response to @{user}: {response}")

    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            "info": "#0099FF",
            "normal": "#00CC99",
            "urgent": "#FFAA00",
            "critical": "#FF3333",
        }
        return colors.get(severity, "#00CC99")
