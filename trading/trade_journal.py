"""Trade Journal - Complete trade history and analysis"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class JournalEntry:
    """A trade journal entry"""
    trade_id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    stop_loss: float = 0.0
    take_profit: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0
    strategy: str = ""
    notes: str = ""
    commission: float = 0.0
    slippage: float = 0.0


class TradeJournal:
    """Complete trade history and analysis"""

    def __init__(self):
        self.entries: List[JournalEntry] = []

    def record_trade(self, entry: JournalEntry):
        """Record a trade in journal"""
        self.entries.append(entry)
        logger.info(f"Journal entry recorded: {entry.trade_id}")

    def close_trade(self, trade_id: str, exit_price: float, pnl: float, pnl_percent: float):
        """Mark trade as closed"""
        for entry in self.entries:
            if entry.trade_id == trade_id:
                entry.exit_price = exit_price
                entry.exit_time = datetime.utcnow()
                entry.pnl = pnl
                entry.pnl_percent = pnl_percent
                logger.info(f"Trade closed: {trade_id} P&L: {pnl_percent:.2f}%")
                return

    def get_stats(self) -> Dict:
        """Get trading statistics"""
        closed_trades = [e for e in self.entries if e.exit_time]
        if not closed_trades:
            return {}

        winning = [t for t in closed_trades if t.pnl > 0]
        losing = [t for t in closed_trades if t.pnl <= 0]

        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': len(winning) / len(closed_trades) * 100 if closed_trades else 0,
            'total_pnl': sum(t.pnl for t in closed_trades),
            'avg_pnl': sum(t.pnl for t in closed_trades) / len(closed_trades) if closed_trades else 0,
            'best_trade': max(t.pnl for t in closed_trades) if closed_trades else 0,
            'worst_trade': min(t.pnl for t in closed_trades) if closed_trades else 0,
        }

    def export_csv(self, filename: str):
        """Export journal to CSV"""
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=asdict(self.entries[0]).keys())
            writer.writeheader()
            for entry in self.entries:
                writer.writerow(asdict(entry))
        logger.info(f"Journal exported to {filename}")
