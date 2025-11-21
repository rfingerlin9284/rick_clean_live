#!/usr/bin/env python3
"""
RBOTzilla UNI - Strategy Pack Manager
Strategy aggregation, voting, and consensus system
PIN: 841921

This module provides:
- Strategy registration and management
- Signal aggregation from multiple strategies
- Confidence-based voting system
- Consensus thresholds and filtering
- Integration with regime overlays
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import logging


@dataclass
class AggregatedSignal:
    """Aggregated signal from multiple strategies"""
    timestamp: pd.Timestamp
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    stop_loss: float
    take_profit: float
    consensus_confidence: float
    risk_reward: float
    contributing_strategies: List[str]
    strategy_votes: Dict[str, float]
    signal_count: int
    avg_confidence: float


class StrategyPackManager:
    """
    Strategy Pack Manager
    
    Manages multiple trading strategies, aggregates their signals,
    and provides consensus-based filtering.
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Strategy Pack Manager with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Strategy Pack Manager")
        
        self.pin_verified = True
        self.name = "StrategyPackManager"
        
        # Registered strategies
        self.strategies = {}
        
        # Consensus parameters
        self.min_confidence = 0.60  # Minimum confidence per strategy
        self.min_strategies = 2  # Minimum strategies agreeing
        self.consensus_threshold = 0.65  # Minimum consensus confidence
        
        # Strategy weights (can be adjusted based on performance)
        self.strategy_weights = {}
        
        self.logger = logging.getLogger("StrategyPackManager")
        self.logger.info("Strategy Pack Manager initialized")
    
    def register_strategy(self, strategy: Any, weight: float = 1.0):
        """
        Register a trading strategy
        
        Args:
            strategy: Strategy instance (must have generate_signals method)
            weight: Strategy weight for voting (default: 1.0)
        """
        if not hasattr(strategy, 'generate_signals'):
            raise ValueError(f"Strategy must have generate_signals method")
        
        if not hasattr(strategy, 'name'):
            raise ValueError(f"Strategy must have name attribute")
        
        self.strategies[strategy.name] = strategy
        self.strategy_weights[strategy.name] = weight
        
        self.logger.info(f"Registered strategy: {strategy.name} (weight: {weight})")
    
    def generate_consensus_signals(self, data: pd.DataFrame,
                                   apply_regime_filter: bool = True) -> List[AggregatedSignal]:
        """
        Generate consensus signals from all registered strategies
        
        Args:
            data: Market data DataFrame
            apply_regime_filter: Whether to filter by regime compatibility
            
        Returns:
            List of AggregatedSignal objects
        """
        if not self.strategies:
            self.logger.warning("No strategies registered")
            return []
        
        # Collect signals from all strategies
        all_signals = {}
        
        for strategy_name, strategy in self.strategies.items():
            try:
                signals = strategy.generate_signals(data)
                all_signals[strategy_name] = signals
                self.logger.info(f"{strategy_name}: Generated {len(signals)} signals")
            except Exception as e:
                self.logger.error(f"Error generating signals from {strategy_name}: {e}")
                all_signals[strategy_name] = []
        
        # Aggregate signals by timestamp and direction
        aggregated = self._aggregate_signals(all_signals)
        
        # Filter by consensus requirements
        consensus_signals = self._filter_by_consensus(aggregated)
        
        self.logger.info(f"Generated {len(consensus_signals)} consensus signals "
                        f"from {len(self.strategies)} strategies")
        
        return consensus_signals
    
    def _aggregate_signals(self, all_signals: Dict[str, List]) -> Dict[Tuple, Dict]:
        """
        Aggregate signals by timestamp and direction
        
        Returns dictionary keyed by (timestamp, direction)
        """
        signal_groups = defaultdict(lambda: {
            'signals': [],
            'strategies': [],
            'confidences': [],
            'entry_prices': [],
            'stop_losses': [],
            'take_profits': [],
            'risk_rewards': []
        })
        
        # Group signals by timestamp and direction
        for strategy_name, signals in all_signals.items():
            for signal in signals:
                # Create key from timestamp and direction
                key = (signal.timestamp, signal.direction)
                
                # Add signal data
                signal_groups[key]['signals'].append(signal)
                signal_groups[key]['strategies'].append(strategy_name)
                signal_groups[key]['confidences'].append(signal.confidence)
                signal_groups[key]['entry_prices'].append(signal.entry_price)
                signal_groups[key]['stop_losses'].append(signal.stop_loss)
                signal_groups[key]['take_profits'].append(signal.take_profit)
                signal_groups[key]['risk_rewards'].append(signal.risk_reward)
        
        return signal_groups
    
    def _filter_by_consensus(self, signal_groups: Dict) -> List[AggregatedSignal]:
        """
        Filter aggregated signals by consensus requirements
        
        Args:
            signal_groups: Grouped signals by (timestamp, direction)
            
        Returns:
            List of consensus signals that meet requirements
        """
        consensus_signals = []
        
        for (timestamp, direction), group in signal_groups.items():
            # Check minimum strategy count
            if len(group['strategies']) < self.min_strategies:
                continue
            
            # Calculate weighted consensus confidence
            weighted_confidences = []
            strategy_votes = {}
            
            for i, strategy_name in enumerate(group['strategies']):
                confidence = group['confidences'][i]
                
                # Check minimum confidence threshold
                if confidence < self.min_confidence:
                    continue
                
                weight = self.strategy_weights.get(strategy_name, 1.0)
                weighted_confidences.append(confidence * weight)
                strategy_votes[strategy_name] = confidence
            
            # Check if we still have minimum strategies after filtering
            if len(weighted_confidences) < self.min_strategies:
                continue
            
            # Calculate consensus confidence
            consensus_confidence = np.mean(weighted_confidences)
            
            # Check consensus threshold
            if consensus_confidence < self.consensus_threshold:
                continue
            
            # Calculate average entry/SL/TP (weighted by confidence)
            weights = np.array(group['confidences'])
            weights = weights / weights.sum()  # Normalize
            
            entry_price = np.average(group['entry_prices'], weights=weights)
            stop_loss = np.average(group['stop_losses'], weights=weights)
            take_profit = np.average(group['take_profits'], weights=weights)
            
            # Calculate risk/reward
            if direction == 'LONG':
                risk = entry_price - stop_loss
                reward = take_profit - entry_price
            else:
                risk = stop_loss - entry_price
                reward = entry_price - take_profit
            
            risk_reward = reward / risk if risk > 0 else 0
            
            # Create aggregated signal
            signal = AggregatedSignal(
                timestamp=timestamp,
                direction=direction,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                consensus_confidence=consensus_confidence,
                risk_reward=risk_reward,
                contributing_strategies=group['strategies'],
                strategy_votes=strategy_votes,
                signal_count=len(group['strategies']),
                avg_confidence=np.mean(group['confidences'])
            )
            
            consensus_signals.append(signal)
        
        return consensus_signals
    
    def update_strategy_weights(self, performance_metrics: Dict[str, float]):
        """
        Update strategy weights based on performance
        
        Args:
            performance_metrics: Dict of {strategy_name: performance_score}
                                Performance score should be 0-1
        """
        for strategy_name, score in performance_metrics.items():
            if strategy_name in self.strategy_weights:
                # Adjust weight based on performance (0.5 to 1.5 range)
                new_weight = 0.5 + score
                self.strategy_weights[strategy_name] = new_weight
                self.logger.info(f"Updated {strategy_name} weight to {new_weight:.2f}")
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get statistics about registered strategies"""
        return {
            'total_strategies': len(self.strategies),
            'strategy_names': list(self.strategies.keys()),
            'strategy_weights': self.strategy_weights.copy(),
            'min_confidence': self.min_confidence,
            'min_strategies': self.min_strategies,
            'consensus_threshold': self.consensus_threshold
        }
    
    def set_consensus_parameters(self, min_confidence: Optional[float] = None,
                                 min_strategies: Optional[int] = None,
                                 consensus_threshold: Optional[float] = None):
        """
        Update consensus parameters
        
        Args:
            min_confidence: Minimum per-strategy confidence (0-1)
            min_strategies: Minimum number of agreeing strategies
            consensus_threshold: Minimum consensus confidence (0-1)
        """
        if min_confidence is not None:
            self.min_confidence = min_confidence
            self.logger.info(f"Updated min_confidence to {min_confidence}")
        
        if min_strategies is not None:
            self.min_strategies = min_strategies
            self.logger.info(f"Updated min_strategies to {min_strategies}")
        
        if consensus_threshold is not None:
            self.consensus_threshold = consensus_threshold
            self.logger.info(f"Updated consensus_threshold to {consensus_threshold}")


def create_default_pack_manager() -> StrategyPackManager:
    """
    Create pack manager with all available strategies registered
    
    Returns:
        StrategyPackManager with default strategies
    """
    from .trap_reversal_scalper import create_trap_reversal_scalper
    from .ema_scalper import create_ema_scalper
    from .price_action_holy_grail import create_price_action_holy_grail
    from .fib_confluence import create_fib_confluence
    
    manager = StrategyPackManager(pin=841921)
    
    # Register strategies with equal weights initially
    manager.register_strategy(create_trap_reversal_scalper(), weight=1.0)
    manager.register_strategy(create_ema_scalper(), weight=1.0)
    manager.register_strategy(create_price_action_holy_grail(), weight=1.0)
    manager.register_strategy(create_fib_confluence(), weight=1.0)
    
    return manager


# Convenience function for quick testing
def test_pack_manager(data: pd.DataFrame) -> List[AggregatedSignal]:
    """
    Quick test of pack manager with sample data
    
    Args:
        data: Market data DataFrame
        
    Returns:
        List of consensus signals
    """
    manager = create_default_pack_manager()
    return manager.generate_consensus_signals(data)
