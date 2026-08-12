"""Backtester - Historical testing of strategies"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class BacktestResults:
    """Results from backtest"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration_days: float


class Backtester:
    """Backtests strategies against historical data"""

    def __init__(self):
        self.backtest_results: Dict[str, BacktestResults] = {}

    def backtest_strategy(self, strategy_name: str, data: pd.DataFrame, 
                          signal_func) -> BacktestResults:
        """Run backtest on strategy"""
        
        trades = []
        current_position = None
        
        for i in range(100, len(data)):
            historical_data = data.iloc[:i]
            
            # Generate signal
            signal = signal_func(historical_data)
            
            # Enter trade
            if signal and not current_position:
                current_position = {
                    'entry_price': signal.entry_price,
                    'entry_index': i,
                    'stop': signal.stop_price,
                    'target': signal.target_price,
                }
            
            # Check exit conditions
            if current_position:
                current_price = data['Close'].iloc[i]
                
                # Stop loss hit
                if current_price <= current_position['stop']:
                    trade = self._close_trade(current_position, current_price, i, data)
                    trades.append(trade)
                    current_position = None
                
                # Take profit hit
                elif current_price >= current_position['target']:
                    trade = self._close_trade(current_position, current_price, i, data)
                    trades.append(trade)
                    current_position = None
        
        # Calculate metrics
        results = self._calculate_metrics(trades, data)
        self.backtest_results[strategy_name] = results
        
        logger.info(f"Backtest {strategy_name}: {results.total_trades} trades, {results.win_rate:.1%} win rate, {results.total_return:.2%} return")
        return results

    def _close_trade(self, position: Dict, exit_price: float, exit_index: int, data: pd.DataFrame) -> Dict:
        """Close a trade and calculate P&L"""
        pnl = (exit_price - position['entry_price']) * 100  # Simplified
        days = exit_index - position['entry_index']
        return {
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'pnl': pnl,
            'pnl_percent': (exit_price - position['entry_price']) / position['entry_price'] * 100,
            'duration_days': days,
        }

    def _calculate_metrics(self, trades: List[Dict], data: pd.DataFrame) -> BacktestResults:
        """Calculate performance metrics"""
        if not trades:
            return BacktestResults(
                total_trades=0, winning_trades=0, losing_trades=0,
                win_rate=0, total_return=0, sharpe_ratio=0, max_drawdown=0, avg_trade_duration_days=0
            )
        
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]
        
        returns = [t['pnl_percent'] / 100 for t in trades]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / (running_max + 1e-8)
        max_dd = np.min(drawdown) if len(drawdown) > 0 else 0
        
        return BacktestResults(
            total_trades=len(trades),
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=len(wins) / len(trades) if trades else 0,
            total_return=sum(t['pnl_percent'] for t in trades) / 100,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            avg_trade_duration_days=np.mean([t['duration_days'] for t in trades])
        )
