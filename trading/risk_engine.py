"""Risk Engine - Position sizing and risk management (hard stops)"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskParameters:
    """Risk management parameters (CANNOT BE OVERRIDDEN BY AI)"""
    account_size: float = 100000
    max_risk_per_trade: float = 0.005  # 0.5% per trade
    max_position_size: float = 0.20  # 20% of account
    max_daily_loss: float = 0.02  # 2% daily max loss
    max_open_positions: int = 5
    min_reward_risk_ratio: float = 2.0


class RiskEngine:
    """Hard-coded risk management (AI cannot override)"""

    def __init__(self, params: RiskParameters = None):
        self.params = params or RiskParameters()
        self.daily_loss = 0.0
        self.open_positions = 0

    def validate_trade(self, entry_price: float, stop_price: float, 
                      target_price: float, quantity: float) -> Tuple[bool, str]:
        """Validate if trade meets risk criteria. AI CANNOT OVERRIDE."""
        
        # Check max positions
        if self.open_positions >= self.params.max_open_positions:
            return False, f"Max open positions ({self.params.max_open_positions}) reached"

        # Calculate risk/reward
        risk = abs(entry_price - stop_price) * quantity
        reward = abs(target_price - entry_price) * quantity

        if risk > (self.params.account_size * self.params.max_risk_per_trade):
            return False, f"Risk ${risk:.2f} exceeds max ${self.params.account_size * self.params.max_risk_per_trade:.2f}"

        if reward > 0 and reward / risk < self.params.min_reward_risk_ratio:
            return False, f"Reward:Risk ratio {reward/risk:.2f} below minimum {self.params.min_reward_risk_ratio}"

        # Check daily loss limit
        if self.daily_loss + risk > (self.params.account_size * self.params.max_daily_loss):
            return False, f"Daily loss limit would be exceeded"

        position_size_percent = (entry_price * quantity) / self.params.account_size
        if position_size_percent > self.params.max_position_size:
            return False, f"Position size {position_size_percent:.1%} exceeds max {self.params.max_position_size:.1%}"

        return True, "Trade approved"

    def record_daily_loss(self, loss: float):
        """Record daily loss (cannot be overridden)"""
        self.daily_loss += loss
        if self.daily_loss > (self.params.account_size * self.params.max_daily_loss):
            logger.warning(f"DAILY LOSS LIMIT EXCEEDED: {self.daily_loss:.2f}")

    def reset_daily(self):
        """Reset daily loss tracking"""
        self.daily_loss = 0.0
        self.open_positions = 0
