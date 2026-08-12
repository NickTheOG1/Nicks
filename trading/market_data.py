"""Market Data Feed - Fetches real-time and historical price data"""

import yfinance as yf
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MarketDataFeed:
    """Real-time and historical market data"""

    def __init__(self, cache_minutes: int = 5):
        self.cache_minutes = cache_minutes
        self.cache: Dict = {}
        self.cache_timestamps: Dict = {}
        self.watchlist = [
            'SPY', 'QQQ', 'IWM', 'DIA', 'AAPL', 'MSFT', 'NVDA', 'AMZN',
            'META', 'GOOGL', 'TSLA', 'AMD', 'AVGO', 'NFLX', 'PLTR',
            'COIN', 'BTC-USD', 'ETH-USD'
        ]

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest price for symbol"""
        try:
            # Check cache
            if self._is_cached(symbol):
                return self.cache[symbol]['close']

            # Fetch from yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                price = data['Close'].iloc[-1]
                self._cache_data(symbol, {'close': price})
                return price
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
        return None

    def get_ohlcv(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """Get OHLCV data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data[['Open', 'High', 'Low', 'Close', 'Volume']]
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return None

    def get_volatility(self, symbol: str, period: int = 20) -> Optional[float]:
        """Calculate historical volatility"""
        try:
            data = self.get_ohlcv(symbol, period='3mo')
            if data is not None and len(data) >= period:
                returns = data['Close'].pct_change().tail(period)
                return returns.std() * (252 ** 0.5)  # Annualized
        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol}: {e}")
        return None

    def scan_watchlist(self) -> Dict[str, Dict]:
        """Scan all watchlist symbols"""
        results = {}
        for symbol in self.watchlist:
            price = self.get_latest_price(symbol)
            vol = self.get_volatility(symbol)
            if price and vol:
                results[symbol] = {'price': price, 'volatility': vol}
        return results

    def _is_cached(self, symbol: str) -> bool:
        """Check if data is fresh in cache"""
        if symbol not in self.cache_timestamps:
            return False
        age = (datetime.utcnow() - self.cache_timestamps[symbol]).total_seconds() / 60
        return age < self.cache_minutes

    def _cache_data(self, symbol: str, data: Dict):
        """Store data in cache"""
        self.cache[symbol] = data
        self.cache_timestamps[symbol] = datetime.utcnow()
