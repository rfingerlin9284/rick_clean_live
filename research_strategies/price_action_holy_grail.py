#!/usr/bin/env python3
"""
RBOTzilla UNI - Price Action Holy Grail Strategy
Consolidation breakouts with engulfing pattern confirmation
PIN: 841921

Strategy Logic:
1. Detect tight consolidation patterns (10+ bars, <0.5% range)
2. Identify engulfing candle patterns
3. Trigger on breakout above/below consolidation with volume
4. Use consolidation range for stop loss placement
5. Dynamic take profit based on recent volatility

Parameters:
- consolidation_bars: 10
- tight_range_pct: 0.005 (0.5%)
- min_body_atr: 0.1 (engulfing minimum size)
- volume_threshold: 1.5x
- min_lookback: 50
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging


@dataclass
class PriceActionSignal:
    """Price action signal output"""
    timestamp: pd.Timestamp
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_reward: float
    pattern_type: str  # 'consolidation_breakout', 'engulfing', 'combined'
    consolidation_duration: int
    range_tightness: float
    volume_factor: float


class PriceActionHolyGrail:
    """
    Price Action Holy Grail Strategy
    
    Combines tight consolidation detection with engulfing patterns
    for high-probability breakout trades.
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Price Action Holy Grail with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Price Action Holy Grail Strategy")
        
        self.pin_verified = True
        self.name = "PriceActionHolyGrail"
        
        # Strategy parameters
        self.consolidation_bars = 10
        self.tight_range_pct = 0.005  # 0.5%
        self.min_body_atr = 0.1
        self.volume_threshold = 1.5
        self.min_lookback = 50
        self.breakout_confirmation_threshold = 0.2  # 20% of ATR
        
        # Risk management
        self.position_risk_pct = 0.02  # 2%
        self.min_risk_reward = 2.0
        
        self.logger = logging.getLogger(f"PriceActionHolyGrail_{pin}")
        self.logger.info("Price Action Holy Grail Strategy initialized")
    
    def generate_signals(self, data: pd.DataFrame) -> List[PriceActionSignal]:
        """
        Generate price action signals from market data
        
        Args:
            data: DataFrame with columns: open, high, low, close, volume
            
        Returns:
            List of PriceActionSignal objects
        """
        signals = []
        
        # Validate data
        if len(data) < self.min_lookback:
            self.logger.warning(f"Insufficient data: {len(data)} bars < {self.min_lookback} required")
            return signals
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_cols):
            self.logger.error(f"Missing required columns. Need: {required_cols}")
            return signals
        
        # Calculate technical indicators
        from .indicators import calculate_atr, calculate_volume_spike
        from .patterns import detect_consolidation, detect_engulfing_patterns
        
        atr = calculate_atr(data['high'], data['low'], data['close'])
        is_consolidating = detect_consolidation(
            data['high'], 
            data['low'], 
            data['close'],
            period=self.consolidation_bars,
            max_range_pct=self.tight_range_pct
        )
        
        engulfing = detect_engulfing_patterns(
            data['open'],
            data['high'],
            data['low'],
            data['close'],
            min_body_atr=self.min_body_atr,
            atr=atr
        )
        
        volume_spikes = calculate_volume_spike(
            data['volume'],
            period=20,
            threshold=self.volume_threshold
        )
        
        # Calculate consolidation highs and lows
        consol_high = data['high'].rolling(window=self.consolidation_bars).max()
        consol_low = data['low'].rolling(window=self.consolidation_bars).min()
        consol_range = consol_high - consol_low
        
        # Detect breakouts from consolidation
        # Bullish: price breaks above consolidation high
        bullish_breakout = (
            (data['close'] > consol_high.shift(1)) &
            is_consolidating.shift(1) &
            volume_spikes
        )
        
        # Bearish: price breaks below consolidation low
        bearish_breakout = (
            (data['close'] < consol_low.shift(1)) &
            is_consolidating.shift(1) &
            volume_spikes
        )
        
        # Process bullish signals (consolidation breakout OR engulfing)
        for idx in data.index:
            i = data.index.get_loc(idx)
            
            # Skip early bars
            if i < self.consolidation_bars + 1:
                continue
            
            # Check for bullish patterns
            is_bullish_breakout = bullish_breakout.iloc[i]
            is_bullish_engulfing = engulfing['bullish'].iloc[i]
            
            if not (is_bullish_breakout or is_bullish_engulfing):
                continue
            
            # Determine pattern type
            if is_bullish_breakout and is_bullish_engulfing:
                pattern_type = 'combined'
                confidence_boost = 0.2
            elif is_bullish_breakout:
                pattern_type = 'consolidation_breakout'
                confidence_boost = 0.1
            else:
                pattern_type = 'engulfing'
                confidence_boost = 0.0
            
            # Calculate entry, SL, TP
            entry_price = data['close'].iloc[i]
            
            # Stop loss below consolidation low or recent low
            if is_bullish_breakout:
                stop_loss = consol_low.iloc[i - 1] - (atr.iloc[i] * 0.2)
            else:
                stop_loss = data['low'].iloc[i] - (atr.iloc[i] * 0.5)
            
            risk = entry_price - stop_loss
            
            # Skip if risk is too small
            if risk <= 0 or risk > atr.iloc[i] * 2:
                continue
            
            # Take profit based on risk/reward
            take_profit = entry_price + (risk * self.min_risk_reward)
            risk_reward = (take_profit - entry_price) / risk
            
            # Calculate consolidation metrics
            if is_bullish_breakout:
                consol_duration = self.consolidation_bars
                range_tightness = (consol_range.iloc[i - 1] / entry_price) if entry_price > 0 else 0
            else:
                consol_duration = 0
                range_tightness = 0
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                volume_factor=data['volume'].iloc[i] / data['volume'].rolling(20).mean().iloc[i],
                range_tightness=range_tightness,
                has_engulfing=is_bullish_engulfing,
                has_breakout=is_bullish_breakout,
                confidence_boost=confidence_boost
            )
            
            # Create signal
            signal = PriceActionSignal(
                timestamp=idx,
                direction='LONG',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                risk_reward=risk_reward,
                pattern_type=pattern_type,
                consolidation_duration=consol_duration,
                range_tightness=range_tightness,
                volume_factor=data['volume'].iloc[i] / data['volume'].rolling(20).mean().iloc[i]
            )
            
            signals.append(signal)
            self.logger.info(f"Bullish PA signal: {signal.pattern_type} at {signal.entry_price:.5f}, "
                           f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
        
        # Process bearish signals
        for idx in data.index:
            i = data.index.get_loc(idx)
            
            # Skip early bars
            if i < self.consolidation_bars + 1:
                continue
            
            # Check for bearish patterns
            is_bearish_breakout = bearish_breakout.iloc[i]
            is_bearish_engulfing = engulfing['bearish'].iloc[i]
            
            if not (is_bearish_breakout or is_bearish_engulfing):
                continue
            
            # Determine pattern type
            if is_bearish_breakout and is_bearish_engulfing:
                pattern_type = 'combined'
                confidence_boost = 0.2
            elif is_bearish_breakout:
                pattern_type = 'consolidation_breakout'
                confidence_boost = 0.1
            else:
                pattern_type = 'engulfing'
                confidence_boost = 0.0
            
            # Calculate entry, SL, TP
            entry_price = data['close'].iloc[i]
            
            # Stop loss above consolidation high or recent high
            if is_bearish_breakout:
                stop_loss = consol_high.iloc[i - 1] + (atr.iloc[i] * 0.2)
            else:
                stop_loss = data['high'].iloc[i] + (atr.iloc[i] * 0.5)
            
            risk = stop_loss - entry_price
            
            # Skip if risk is too small
            if risk <= 0 or risk > atr.iloc[i] * 2:
                continue
            
            # Take profit based on risk/reward
            take_profit = entry_price - (risk * self.min_risk_reward)
            risk_reward = (entry_price - take_profit) / risk
            
            # Calculate consolidation metrics
            if is_bearish_breakout:
                consol_duration = self.consolidation_bars
                range_tightness = (consol_range.iloc[i - 1] / entry_price) if entry_price > 0 else 0
            else:
                consol_duration = 0
                range_tightness = 0
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                volume_factor=data['volume'].iloc[i] / data['volume'].rolling(20).mean().iloc[i],
                range_tightness=range_tightness,
                has_engulfing=is_bearish_engulfing,
                has_breakout=is_bearish_breakout,
                confidence_boost=confidence_boost
            )
            
            # Create signal
            signal = PriceActionSignal(
                timestamp=idx,
                direction='SHORT',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                risk_reward=risk_reward,
                pattern_type=pattern_type,
                consolidation_duration=consol_duration,
                range_tightness=range_tightness,
                volume_factor=data['volume'].iloc[i] / data['volume'].rolling(20).mean().iloc[i]
            )
            
            signals.append(signal)
            self.logger.info(f"Bearish PA signal: {signal.pattern_type} at {signal.entry_price:.5f}, "
                           f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
        
        return signals
    
    def _calculate_confidence(self, volume_factor: float, range_tightness: float,
                             has_engulfing: bool, has_breakout: bool,
                             confidence_boost: float) -> float:
        """
        Calculate signal confidence (0-1)
        
        Weights:
        - Volume confirmation: 35%
        - Range tightness: 25%
        - Pattern type: 40% (engulfing + breakout is best)
        """
        # Volume score (normalize to 0-1)
        volume_score = min(1.0, (volume_factor - 1.0) / 2.0)
        
        # Range tightness score (tighter = better)
        # 0.3% range = maximum confidence
        if range_tightness > 0:
            tightness_score = 1.0 - min(1.0, range_tightness / 0.003)
        else:
            tightness_score = 0.5
        
        # Pattern score
        pattern_score = 0.0
        if has_breakout:
            pattern_score += 0.5
        if has_engulfing:
            pattern_score += 0.5
        
        # Weighted average
        confidence = (
            volume_score * 0.35 +
            tightness_score * 0.25 +
            pattern_score * 0.40 +
            confidence_boost
        )
        
        return min(1.0, max(0.0, confidence))
    
    def get_parameters(self) -> Dict:
        """Get current strategy parameters"""
        return {
            'name': self.name,
            'consolidation_bars': self.consolidation_bars,
            'tight_range_pct': self.tight_range_pct,
            'min_body_atr': self.min_body_atr,
            'volume_threshold': self.volume_threshold,
            'min_lookback': self.min_lookback,
            'breakout_confirmation_threshold': self.breakout_confirmation_threshold,
            'position_risk_pct': self.position_risk_pct,
            'min_risk_reward': self.min_risk_reward
        }


# Convenience function for easy integration
def create_price_action_holy_grail(**kwargs) -> PriceActionHolyGrail:
    """Create Price Action Holy Grail with optional parameter overrides"""
    strategy = PriceActionHolyGrail()
    
    # Override parameters if provided
    for key, value in kwargs.items():
        if hasattr(strategy, key):
            setattr(strategy, key, value)
    
    return strategy
