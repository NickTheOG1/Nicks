"""Trading Strategies - Multiple algorithmic strategies"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    SHORT = "SHORT"
    HOLD = "HOLD"


@dataclass
class Signal:
    """Trading signal from strategy"""
    strategy_name: str
    symbol: str
    signal_type: SignalType
    confidence: float  # 0-1
    entry_price: float
    stop_price: float
    target_price: float
    reasoning: str
    timestamp: str = None


class StrategyEngine:
    """Multiple trading strategies"""

    def __init__(self):
        self.strategies = {
            'trend_following': self.trend_following_strategy,
            'momentum': self.momentum_strategy,
            'mean_reversion': self.mean_reversion_strategy,
            'breakout': self.breakout_strategy,
            'volatility': self.volatility_strategy,
        }

    def analyze(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        """Run all strategies and return signals"""
        signals = []
        for name, strategy_func in self.strategies.items():
            signal = strategy_func(symbol, data)
            if signal:
                signals.append(signal)
        return signals

    def trend_following_strategy(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Trend Following: Follow price trends"""
        if len(data) < 50:
            return None

        close = data['Close']
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()

        if sma20.iloc[-1] > sma50.iloc[-1]:
            # Uptrend
            entry = close.iloc[-1]
            stop = close.iloc[-1] * 0.95
            target = close.iloc[-1] * 1.1
            return Signal(
                strategy_name='Trend Following',
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=0.75,
                entry_price=entry,
                stop_price=stop,
                target_price=target,
                reasoning='Price above SMA20 and SMA50 uptrend'
            )
        return None

    def momentum_strategy(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Momentum: Strong price moves"""
        if len(data) < 14:
            return None

        close = data['Close']
        rsi = self._calculate_rsi(close)

        if rsi[-1] > 70:
            # Overbought - potential pullback
            entry = close.iloc[-1]
            target = entry * 1.05
            stop = entry * 0.98
            return Signal(
                strategy_name='Momentum',
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=0.7,
                entry_price=entry,
                stop_price=stop,
                target_price=target,
                reasoning='RSI > 70 (overbought)'
            )
        return None

    def mean_reversion_strategy(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Mean Reversion: Prices return to average"""
        if len(data) < 20:
            return None

        close = data['Close']
        sma = close.rolling(20).mean()
        std = close.rolling(20).std()

        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        if close.iloc[-1] < lower_band.iloc[-1]:
            # Price below lower band - expect reversion up
            entry = close.iloc[-1]
            return Signal(
                strategy_name='Mean Reversion',
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=0.65,
                entry_price=entry,
                stop_price=lower_band.iloc[-1] * 0.99,
                target_price=sma.iloc[-1],
                reasoning='Price below 2-sigma band'
            )
        return None

    def breakout_strategy(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Breakout: Price breaks resistance/support"""
        if len(data) < 20:
            return None

        close = data['Close']
        high = data['High'].rolling(20).max()
        low = data['Low'].rolling(20).min()

        if close.iloc[-1] > high.iloc[-2]:
            # Breakout above 20-day high
            entry = close.iloc[-1]
            return Signal(
                strategy_name='Breakout',
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=0.72,
                entry_price=entry,
                stop_price=high.iloc[-20],
                target_price=entry * 1.15,
                reasoning='Price broke above 20-day high'
            )
        return None

    def volatility_strategy(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Volatility: Trade on volatility changes"""
        if len(data) < 30:
            return None

        returns = data['Close'].pct_change()
        current_vol = returns.tail(10).std() * np.sqrt(252)
        avg_vol = returns.tail(30).std() * np.sqrt(252)

        if current_vol > avg_vol * 1.5:
            # High volatility
            entry = data['Close'].iloc[-1]
            return Signal(
                strategy_name='Volatility',
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=0.6,
                entry_price=entry,
                stop_price=entry * 0.97,
                target_price=entry * 1.08,
                reasoning=f'Volatility spike: {current_vol:.1%} vs avg {avg_vol:.1%}'
            )
        return None

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
