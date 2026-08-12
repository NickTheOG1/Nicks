"""Signal Engine - Ranks and scores trading signals"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class SignalEngine:
    """Ranks signals by confidence and filters low-quality ones"""

    def __init__(self, confidence_threshold: float = 0.60):
        self.confidence_threshold = confidence_threshold
        self.signal_history = []

    def rank_signals(self, signals: List) -> List[Tuple]:
        """Rank signals by confidence and reward:risk"""
        ranked = []
        for signal in signals:
            score = self._calculate_score(signal)
            ranked.append((score, signal))
        
        # Sort by score descending
        ranked.sort(key=lambda x: x[0], reverse=True)
        return ranked

    def filter_signals(self, signals: List) -> List:
        """Filter signals above confidence threshold"""
        ranked = self.rank_signals(signals)
        filtered = [signal for score, signal in ranked if score >= self.confidence_threshold]
        logger.info(f"Filtered {len(signals)} signals down to {len(filtered)} high-confidence signals")
        return filtered

    def _calculate_score(self, signal) -> float:
        """Calculate overall signal score"""
        # Base confidence
        score = signal.confidence
        
        # Reward:Risk ratio bonus
        reward_risk = abs(signal.target_price - signal.entry_price) / abs(signal.entry_price - signal.stop_price)
        score += min(reward_risk / 10, 0.2)  # Up to 0.2 bonus
        
        # Cap at 1.0
        return min(score, 1.0)
