"""Paper Broker - Simulates trades with realistic execution"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


class TradeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class PaperTrade:
    """A paper trade execution"""
    trade_id: str
    symbol: str
    side: str  # BUY, SHORT
    quantity: float
    entry_price: float
    stop_loss: float
    take_profit: float
    opened_at: datetime
    closed_at: Optional[datetime] = None
    exit_price: Optional[float] = None
    status: TradeStatus = TradeStatus.OPEN
    pnl: float = 0.0
    pnl_percent: float = 0.0
    commission: float = 0.0
    slippage: float = 0.0


class PaperBroker:
    """Paper trading simulation with realistic execution"""

    def __init__(self, account_value: float = 100000, commission_rate: float = 0.001):
        self.account_value = account_value
        self.commission_rate = commission_rate
        self.trades: Dict[str, PaperTrade] = {}
        self.trade_counter = 0
        self.closed_trades: List[PaperTrade] = []

    def submit_trade(self, symbol: str, side: str, quantity: float, 
                     entry_price: float, stop_loss: float, take_profit: float) -> str:
        """Submit a new paper trade"""
        self.trade_counter += 1
        trade_id = f"PAPER-{self.trade_counter:05d}"

        # Simulate slippage
        slippage = self._calculate_slippage(entry_price)
        actual_entry = entry_price + slippage

        # Calculate commission
        commission = (actual_entry * quantity) * self.commission_rate

        trade = PaperTrade(
            trade_id=trade_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=actual_entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            opened_at=datetime.utcnow(),
            commission=commission,
            slippage=slippage,
        )

        self.trades[trade_id] = trade
        logger.info(f"Paper trade opened: {trade_id} {side} {quantity} {symbol} @ ${actual_entry:.2f}")
        return trade_id

    def close_trade(self, trade_id: str, exit_price: float) -> bool:
        """Close a paper trade"""
        if trade_id not in self.trades:
            return False

        trade = self.trades[trade_id]
        if trade.status == TradeStatus.CLOSED:
            return False

        # Simulate slippage on exit
        exit_slippage = self._calculate_slippage(exit_price)
        actual_exit = exit_price + exit_slippage

        # Calculate P&L
        if trade.side == 'BUY':
            pnl = (actual_exit - trade.entry_price) * trade.quantity - (trade.commission * 2)
        else:  # SHORT
            pnl = (trade.entry_price - actual_exit) * trade.quantity - (trade.commission * 2)

        pnl_percent = (pnl / (trade.entry_price * trade.quantity)) * 100

        trade.exit_price = actual_exit
        trade.closed_at = datetime.utcnow()
        trade.status = TradeStatus.CLOSED
        trade.pnl = pnl
        trade.pnl_percent = pnl_percent

        # Move to closed
        del self.trades[trade_id]
        self.closed_trades.append(trade)

        # Update account value
        self.account_value += pnl

        logger.info(f"Trade closed: {trade_id} P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
        return True

    def check_stop_loss(self, trade_id: str, current_price: float) -> bool:
        """Check if stop loss is hit"""
        if trade_id not in self.trades:
            return False

        trade = self.trades[trade_id]
        if trade.side == 'BUY':
            return current_price <= trade.stop_loss
        else:  # SHORT
            return current_price >= trade.stop_loss

    def check_take_profit(self, trade_id: str, current_price: float) -> bool:
        """Check if take profit is hit"""
        if trade_id not in self.trades:
            return False

        trade = self.trades[trade_id]
        if trade.side == 'BUY':
            return current_price >= trade.take_profit
        else:  # SHORT
            return current_price <= trade.take_profit

    def get_performance(self) -> Dict:
        """Get account performance summary"""
        all_trades = list(self.trades.values()) + self.closed_trades
        closed = [t for t in all_trades if t.status == TradeStatus.CLOSED]

        if not closed:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
            }

        wins = [t for t in closed if t.pnl > 0]
        losses = [t for t in closed if t.pnl < 0]

        return {
            'total_trades': len(closed),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(closed) * 100,
            'total_pnl': sum(t.pnl for t in closed),
            'avg_pnl': sum(t.pnl for t in closed) / len(closed),
        }

    def _calculate_slippage(self, price: float) -> float:
        """Simulate realistic slippage"""
        # Random slippage between -0.5% and +0.5%
        slippage_percent = random.uniform(-0.005, 0.005)
        return price * slippage_percent
