#!/usr/bin/env python3
"""
RBOTzilla UNI - EMA Scalper Strategy
EMA 50/200 crossover scalping with tight stops
PIN: 841921

Strategy Logic:
1. Detect EMA 50/200 crossovers for trend direction
2. Enter on crossover confirmation
3. Use tight stops (0.3%) and targets (0.6%) for 2:1 R:R
4. Require clear EMA separation for trend confirmation
5. Exit if position exceeds duration limit

Parameters (Adjusted for 2:1 R:R):
- ema_fast: 50
- ema_slow: 200
- sl_pct: 0.003 (0.3%)
- tp_pct: 0.006 (0.6%)
- min_ema_separation_pct: 0.001 (0.1%)
- confirmation_bars: 2
- max_duration_minutes: 15
- lookback_bars: 210
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging


@dataclass
class EMAScalperSignal:
    """EMA scalper signal output"""
    timestamp: pd.Timestamp
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_reward: float
    signal_type: str  # 'bullish_crossover' or 'bearish_crossover'
    ema_separation_pct: float
    trend_strength: float


class EMAScalper:
    """
    EMA Scalper Strategy
    
    Trades EMA 50/200 crossovers with tight stop loss and take profit
    for quick scalping opportunities.
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize EMA Scalper with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for EMA Scalper Strategy")
        
        self.pin_verified = True
        self.name = "EMAScalper"
        
        # Strategy parameters (adjusted for 2:1 R:R - Option A from docs)
        self.ema_fast = 50
        self.ema_slow = 200
        self.sl_pct = 0.003  # 0.3% stop loss
        self.tp_pct = 0.006  # 0.6% take profit (2:1 ratio)
        self.min_ema_separation_pct = 0.001  # 0.1% minimum separation
        self.confirmation_bars = 2  # Require 2 bars confirmation
        self.max_duration_minutes = 15
        self.lookback_bars = 210  # Need 200+ for EMA 200
        
        # Risk management
        self.position_risk_pct = 0.01  # 1% max (reduced from typical 2%)
        
        self.logger = logging.getLogger(f"EMAScalper_{pin}")
        self.logger.info("EMA Scalper Strategy initialized")
        self.logger.info(f"Risk/Reward Ratio: {self.tp_pct/self.sl_pct:.2f}:1")
    
    def generate_signals(self, data: pd.DataFrame) -> List[EMAScalperSignal]:
        """
        Generate EMA scalper signals from market data
        
        Args:
            data: DataFrame with columns: open, high, low, close, volume
            
        Returns:
            List of EMAScalperSignal objects
        """
        signals = []
        
        # Validate data
        if len(data) < self.lookback_bars:
            self.logger.warning(f"Insufficient data: {len(data)} bars < {self.lookback_bars} required")
            return signals
        
        required_cols = ['close']
        if not all(col in data.columns for col in required_cols):
            self.logger.error(f"Missing required columns. Need: {required_cols}")
            return signals
        
        # Calculate EMAs
        from .indicators import calculate_ema
        
        ema_fast = calculate_ema(data['close'], self.ema_fast)
        ema_slow = calculate_ema(data['close'], self.ema_slow)
        
        # Calculate EMA separation percentage
        ema_separation = (ema_fast - ema_slow) / ema_slow
        
        # Detect crossovers
        bullish_cross = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
        bearish_cross = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))
        
        # Require confirmation (multiple bars with EMA fast > slow)
        if self.confirmation_bars > 1:
            # Check that EMA relationship holds for confirmation_bars
            bullish_confirmed = pd.Series(False, index=data.index)
            bearish_confirmed = pd.Series(False, index=data.index)
            
            for i in range(self.confirmation_bars, len(data)):
                # Bullish: EMA fast > slow for last N bars
                if all(ema_fast.iloc[i - j] > ema_slow.iloc[i - j] 
                      for j in range(self.confirmation_bars)):
                    bullish_confirmed.iloc[i] = True
                
                # Bearish: EMA fast < slow for last N bars
                if all(ema_fast.iloc[i - j] < ema_slow.iloc[i - j] 
                      for j in range(self.confirmation_bars)):
                    bearish_confirmed.iloc[i] = True
            
            # Only signal on crossover with confirmation
            bullish_signals = bullish_cross & bullish_confirmed
            bearish_signals = bearish_cross & bearish_confirmed
        else:
            bullish_signals = bullish_cross
            bearish_signals = bearish_cross
        
        # Process bullish signals
        for idx in data.index[bullish_signals]:
            i = data.index.get_loc(idx)
            
            # Check minimum EMA separation
            if abs(ema_separation.iloc[i]) < self.min_ema_separation_pct:
                continue
            
            # Calculate entry, SL, TP
            entry_price = data['close'].iloc[i]
            stop_loss = entry_price * (1 - self.sl_pct)
            take_profit = entry_price * (1 + self.tp_pct)
            
            # Calculate actual R:R
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
            risk_reward = reward / risk if risk > 0 else 0
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                ema_separation=abs(ema_separation.iloc[i]),
                trend_strength=ema_separation.iloc[i]
            )
            
            # Create signal
            signal = EMAScalperSignal(
                timestamp=idx,
                direction='LONG',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                risk_reward=risk_reward,
                signal_type='bullish_crossover',
                ema_separation_pct=ema_separation.iloc[i] * 100,
                trend_strength=ema_separation.iloc[i]
            )
            
            signals.append(signal)
            self.logger.info(f"Bullish EMA signal: {signal.direction} at {signal.entry_price:.5f}, "
                           f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
        
        # Process bearish signals
        for idx in data.index[bearish_signals]:
            i = data.index.get_loc(idx)
            
            # Check minimum EMA separation
            if abs(ema_separation.iloc[i]) < self.min_ema_separation_pct:
                continue
            
            # Calculate entry, SL, TP
            entry_price = data['close'].iloc[i]
            stop_loss = entry_price * (1 + self.sl_pct)
            take_profit = entry_price * (1 - self.tp_pct)
            
            # Calculate actual R:R
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
            risk_reward = reward / risk if risk > 0 else 0
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                ema_separation=abs(ema_separation.iloc[i]),
                trend_strength=-ema_separation.iloc[i]
            )
            
            # Create signal
            signal = EMAScalperSignal(
                timestamp=idx,
                direction='SHORT',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                risk_reward=risk_reward,
                signal_type='bearish_crossover',
                ema_separation_pct=ema_separation.iloc[i] * 100,
                trend_strength=-ema_separation.iloc[i]
            )
            
            signals.append(signal)
            self.logger.info(f"Bearish EMA signal: {signal.direction} at {signal.entry_price:.5f}, "
                           f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
        
        return signals
    
    def _calculate_confidence(self, ema_separation: float, trend_strength: float) -> float:
        """
        Calculate signal confidence (0-1)
        
        Weights:
        - EMA separation (wider = better): 60%
        - Trend strength (directional confirmation): 40%
        """
        # EMA separation score (normalize to 0-1)
        # 0.5% separation = maximum confidence
        separation_score = min(1.0, ema_separation / 0.005)
        
        # Trend strength score (normalize to 0-1)
        # Positive trend_strength for the direction we're trading
        strength_score = min(1.0, abs(trend_strength) / 0.005)
        
        # Weighted average
        confidence = (
            separation_score * 0.60 +
            strength_score * 0.40
        )
        
        return min(1.0, max(0.0, confidence))
    
    def get_parameters(self) -> Dict:
        """Get current strategy parameters"""
        return {
            'name': self.name,
            'ema_fast': self.ema_fast,
            'ema_slow': self.ema_slow,
            'sl_pct': self.sl_pct,
            'tp_pct': self.tp_pct,
            'risk_reward_ratio': self.tp_pct / self.sl_pct,
            'min_ema_separation_pct': self.min_ema_separation_pct,
            'confirmation_bars': self.confirmation_bars,
            'max_duration_minutes': self.max_duration_minutes,
            'lookback_bars': self.lookback_bars,
            'position_risk_pct': self.position_risk_pct
        }


# Convenience function for easy integration
def create_ema_scalper(**kwargs) -> EMAScalper:
    """Create EMA Scalper with optional parameter overrides"""
    strategy = EMAScalper(pin=841921)
    
    # Override parameters if provided
    for key, value in kwargs.items():
        if hasattr(strategy, key):
            setattr(strategy, key, value)
    
    return strategy
