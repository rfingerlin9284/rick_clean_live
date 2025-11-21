#!/usr/bin/env python3
"""
RBOTzilla UNI - Fibonacci Confluence Strategy
Fibonacci retracement zone trading (50% and 61.8% levels)
PIN: 841921

Strategy Logic:
1. Identify swing highs and lows in recent bars
2. Calculate Fibonacci retracement levels (50%, 61.8%)
3. Enter when price pulls back into confluence zone
4. Stop loss below swing low (15% buffer)
5. Take profit at 2:1 risk/reward

Parameters:
- fib_lookback: 10 bars
- fib_50: 0.50 (50% retracement)
- fib_618: 0.618 (61.8% retracement)
- entry_zone: [0.50, 0.618]
- tp_multiple: 2.0
- sl_buffer_pct: -0.15 (15% below swing)
- min_lookback: 15
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class FibConfluenceSignal:
    """Fibonacci confluence signal output"""
    timestamp: pd.Timestamp
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_reward: float
    swing_high: float
    swing_low: float
    fib_50_level: float
    fib_618_level: float
    pullback_depth_pct: float


class FibConfluence:
    """
    Fibonacci Confluence Strategy
    
    Trades pullbacks to key Fibonacci retracement zones (50% and 61.8%)
    with fixed 2:1 risk/reward targets.
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Fibonacci Confluence with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Fibonacci Confluence Strategy")
        
        self.pin_verified = True
        self.name = "FibConfluence"
        
        # Strategy parameters (immutable from docs)
        self.fib_lookback = 10
        self.fib_50 = 0.50
        self.fib_618 = 0.618
        self.entry_zone = [0.50, 0.618]  # Entry between 50% and 61.8%
        self.tp_multiple = 2.0
        self.sl_buffer_pct = -0.15  # 15% below swing low
        self.min_lookback = 15
        
        # Zone tightness requirement
        self.max_zone_width_atr = 0.30
        
        # Risk management
        self.position_risk_pct = 0.02  # 2%
        
        self.logger = logging.getLogger(f"FibConfluence_{pin}")
        self.logger.info("Fibonacci Confluence Strategy initialized")
    
    def generate_signals(self, data: pd.DataFrame) -> List[FibConfluenceSignal]:
        """
        Generate Fibonacci confluence signals from market data
        
        Args:
            data: DataFrame with columns: open, high, low, close, volume
            
        Returns:
            List of FibConfluenceSignal objects
        """
        signals = []
        
        # Validate data
        if len(data) < self.min_lookback:
            self.logger.warning(f"Insufficient data: {len(data)} bars < {self.min_lookback} required")
            return signals
        
        required_cols = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            self.logger.error(f"Missing required columns. Need: {required_cols}")
            return signals
        
        # Calculate ATR for validation
        from .indicators import calculate_atr
        atr = calculate_atr(data['high'], data['low'], data['close'])
        
        # Process each bar looking for Fib setups
        for i in range(self.min_lookback, len(data)):
            # Find swing high and low in lookback window
            lookback_window = slice(max(0, i - self.fib_lookback), i)
            swing_high = data['high'].iloc[lookback_window].max()
            swing_low = data['low'].iloc[lookback_window].min()
            
            # Ensure swing points are far enough apart
            swing_range = swing_high - swing_low
            if swing_range < atr.iloc[i] * 0.5:
                continue
            
            # Calculate Fibonacci levels
            fib_50_level = swing_low + (swing_range * self.fib_50)
            fib_618_level = swing_low + (swing_range * self.fib_618)
            
            # Check zone width (must be tight per guardian rules)
            zone_width = abs(fib_618_level - fib_50_level)
            if zone_width > atr.iloc[i] * self.max_zone_width_atr:
                continue
            
            current_price = data['close'].iloc[i]
            
            # Check for bullish setup (pullback to fib zone after uptrend)
            # Price should have moved above swing high, then pulled back to fib zone
            recent_high = data['high'].iloc[max(0, i - 5):i].max()
            
            if (recent_high > swing_high * 1.002 and  # Recent breakout above swing high
                fib_50_level <= current_price <= fib_618_level):  # Now in fib zone
                
                # Calculate entry, SL, TP
                entry_price = current_price
                stop_loss = swing_low * (1 + self.sl_buffer_pct)  # 15% below swing low
                risk = entry_price - stop_loss
                
                # Skip if risk is invalid
                if risk <= 0:
                    continue
                
                take_profit = entry_price + (risk * self.tp_multiple)
                risk_reward = (take_profit - entry_price) / risk
                
                # Calculate pullback depth
                pullback_depth = (swing_high - current_price) / swing_range
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    pullback_depth=pullback_depth,
                    zone_width=zone_width,
                    atr_value=atr.iloc[i],
                    swing_range=swing_range
                )
                
                # Create signal
                signal = FibConfluenceSignal(
                    timestamp=data.index[i],
                    direction='LONG',
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    risk_reward=risk_reward,
                    swing_high=swing_high,
                    swing_low=swing_low,
                    fib_50_level=fib_50_level,
                    fib_618_level=fib_618_level,
                    pullback_depth_pct=pullback_depth * 100
                )
                
                signals.append(signal)
                self.logger.info(f"Bullish Fib signal: {signal.direction} at {signal.entry_price:.5f}, "
                               f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
            
            # Check for bearish setup (rally to fib zone after downtrend)
            recent_low = data['low'].iloc[max(0, i - 5):i].min()
            
            # For bearish, calculate fib from swing high down
            fib_50_bearish = swing_high - (swing_range * self.fib_50)
            fib_618_bearish = swing_high - (swing_range * self.fib_618)
            
            if (recent_low < swing_low * 0.998 and  # Recent breakdown below swing low
                fib_618_bearish <= current_price <= fib_50_bearish):  # Now in fib zone
                
                # Calculate entry, SL, TP
                entry_price = current_price
                stop_loss = swing_high * (1 - self.sl_buffer_pct)  # 15% above swing high
                risk = stop_loss - entry_price
                
                # Skip if risk is invalid
                if risk <= 0:
                    continue
                
                take_profit = entry_price - (risk * self.tp_multiple)
                risk_reward = (entry_price - take_profit) / risk
                
                # Calculate pullback depth
                pullback_depth = (current_price - swing_low) / swing_range
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    pullback_depth=pullback_depth,
                    zone_width=zone_width,
                    atr_value=atr.iloc[i],
                    swing_range=swing_range
                )
                
                # Create signal
                signal = FibConfluenceSignal(
                    timestamp=data.index[i],
                    direction='SHORT',
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    risk_reward=risk_reward,
                    swing_high=swing_high,
                    swing_low=swing_low,
                    fib_50_level=fib_50_bearish,
                    fib_618_level=fib_618_bearish,
                    pullback_depth_pct=pullback_depth * 100
                )
                
                signals.append(signal)
                self.logger.info(f"Bearish Fib signal: {signal.direction} at {signal.entry_price:.5f}, "
                               f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
        
        return signals
    
    def _calculate_confidence(self, pullback_depth: float, zone_width: float,
                             atr_value: float, swing_range: float) -> float:
        """
        Calculate signal confidence (0-1)
        
        Weights:
        - Pullback depth (closer to golden ratio = better): 40%
        - Zone tightness (tighter = better): 35%
        - Swing range (larger = better): 25%
        """
        # Pullback depth score (50-61.8% is ideal)
        # Score highest when depth is around 0.55 (midpoint of zone)
        ideal_depth = 0.55
        depth_deviation = abs(pullback_depth - ideal_depth)
        depth_score = max(0.0, 1.0 - (depth_deviation / 0.3))
        
        # Zone tightness score (tighter is better)
        # Zone width should be < 0.3 ATR
        zone_ratio = zone_width / atr_value
        tightness_score = max(0.0, 1.0 - (zone_ratio / self.max_zone_width_atr))
        
        # Swing range score (larger swings = clearer pattern)
        # Normalize: 2 ATR swing = max score
        range_score = min(1.0, swing_range / (atr_value * 2))
        
        # Weighted average
        confidence = (
            depth_score * 0.40 +
            tightness_score * 0.35 +
            range_score * 0.25
        )
        
        return min(1.0, max(0.0, confidence))
    
    def get_parameters(self) -> Dict:
        """Get current strategy parameters"""
        return {
            'name': self.name,
            'fib_lookback': self.fib_lookback,
            'fib_50': self.fib_50,
            'fib_618': self.fib_618,
            'entry_zone': self.entry_zone,
            'tp_multiple': self.tp_multiple,
            'sl_buffer_pct': self.sl_buffer_pct,
            'min_lookback': self.min_lookback,
            'max_zone_width_atr': self.max_zone_width_atr,
            'position_risk_pct': self.position_risk_pct
        }


# Convenience function for easy integration
def create_fib_confluence(**kwargs) -> FibConfluence:
    """Create Fibonacci Confluence with optional parameter overrides"""
    strategy = FibConfluence()
    
    # Override parameters if provided
    for key, value in kwargs.items():
        if hasattr(strategy, key):
            setattr(strategy, key, value)
    
    return strategy
