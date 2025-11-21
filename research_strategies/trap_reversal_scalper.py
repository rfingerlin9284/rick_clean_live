#!/usr/bin/env python3
"""
RBOTzilla UNI - Trap Reversal Scalper Strategy
Liquidity trap detection with ATR/RSI confirmation
PIN: 841921

Strategy Logic:
1. Detect liquidity zones (swing highs/lows)
2. Identify false breakouts (liquidity sweeps)
3. Confirm with volume spike and RSI
4. Enter on reversal with 2:1 minimum R:R
5. Use ATR for dynamic stop loss sizing

Parameters:
- atr_period: 14
- rsi_period: 14
- volume_spike_threshold: 1.5x
- rsi_oversold: 30
- rsi_overbought: 70
- min_risk_reward: 2.0
- position_risk_pct: 0.02 (2%)
- lookback_bars: 50
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class TrapReversalSignal:
    """Trap reversal signal output"""
    timestamp: pd.Timestamp
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_reward: float
    trap_type: str  # 'liquidity_sweep_high' or 'liquidity_sweep_low'
    volume_spike_factor: float
    rsi_value: float
    atr_value: float


class TrapReversalScalper:
    """
    Trap Reversal Scalper Strategy
    
    Detects false breakouts (liquidity traps) and trades the reversal
    with volume and RSI confirmation.
    """
    
    def __init__(self, pin: int = 841921):
        """Initialize Trap Reversal Scalper with PIN authentication"""
        if pin != 841921:
            raise ValueError("Invalid PIN for Trap Reversal Scalper Strategy")
        
        self.pin_verified = True
        self.name = "TrapReversalScalper"
        
        # Strategy parameters (from STRATEGY_PARAMETERS_COMPLETE.md)
        self.atr_period = 14
        self.rsi_period = 14
        self.volume_spike_threshold = 1.5
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.min_risk_reward = 2.0
        self.position_risk_pct = 0.02  # 2% max
        self.lookback_bars = 50
        
        # Liquidity detection parameters
        self.liquidity_buffer_atr = 0.2
        self.min_sweep_distance_atr = 0.3
        self.max_sweep_distance_atr = 2.0
        
        self.logger = logging.getLogger(f"TrapReversalScalper_{pin}")
        self.logger.info("Trap Reversal Scalper Strategy initialized")
    
    def generate_signals(self, data: pd.DataFrame) -> List[TrapReversalSignal]:
        """
        Generate trap reversal signals from market data
        
        Args:
            data: DataFrame with columns: open, high, low, close, volume
            
        Returns:
            List of TrapReversalSignal objects
        """
        signals = []
        
        # Validate data
        if len(data) < self.lookback_bars:
            self.logger.warning(f"Insufficient data: {len(data)} bars < {self.lookback_bars} required")
            return signals
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_cols):
            self.logger.error(f"Missing required columns. Need: {required_cols}")
            return signals
        
        # Calculate technical indicators
        from .indicators import calculate_rsi, calculate_atr, calculate_volume_spike
        from .patterns import identify_liquidity_zones, detect_liquidity_sweep
        
        rsi = calculate_rsi(data['close'], self.rsi_period)
        atr = calculate_atr(data['high'], data['low'], data['close'], self.atr_period)
        volume_spikes = calculate_volume_spike(data['volume'], 
                                               period=20, 
                                               threshold=self.volume_spike_threshold)
        
        # Identify liquidity zones
        liquidity_zones = identify_liquidity_zones(
            data['high'], 
            data['low'],
            lookback=self.lookback_bars,
            buffer_atr=self.liquidity_buffer_atr,
            atr=atr
        )
        
        # Detect liquidity sweeps
        sweeps = detect_liquidity_sweep(
            data['high'],
            data['low'],
            data['close'],
            liquidity_zones,
            min_distance_atr=self.min_sweep_distance_atr,
            max_distance_atr=self.max_sweep_distance_atr,
            atr=atr
        )
        
        # Process bullish sweeps (sweep low, reverse up)
        for sweep_data in sweeps['bullish']:
            idx = sweep_data['index']
            
            # Skip if not enough data after sweep
            if idx >= len(data) - 1:
                continue
            
            # Check RSI oversold condition
            if rsi.iloc[idx] > self.rsi_oversold:
                continue
            
            # Check volume spike
            if not volume_spikes.iloc[idx]:
                continue
            
            # Calculate entry, SL, TP
            entry_price = data['close'].iloc[idx]
            stop_loss = data['low'].iloc[idx] - (atr.iloc[idx] * 0.5)
            risk = entry_price - stop_loss
            
            # Ensure minimum risk/reward
            take_profit = entry_price + (risk * self.min_risk_reward)
            risk_reward = (take_profit - entry_price) / risk if risk > 0 else 0
            
            if risk_reward < self.min_risk_reward:
                continue
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_confidence(
                rsi_value=rsi.iloc[idx],
                volume_spike_factor=data['volume'].iloc[idx] / data['volume'].rolling(20).mean().iloc[idx],
                sweep_strength=sweep_data['reversal_strength'],
                zone_strength=sweep_data['zone'].strength
            )
            
            # Create signal
            signal = TrapReversalSignal(
                timestamp=data.index[idx],
                direction='LONG',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                risk_reward=risk_reward,
                trap_type='liquidity_sweep_low',
                volume_spike_factor=data['volume'].iloc[idx] / data['volume'].rolling(20).mean().iloc[idx],
                rsi_value=rsi.iloc[idx],
                atr_value=atr.iloc[idx]
            )
            
            signals.append(signal)
            self.logger.info(f"Bullish trap signal: {signal.direction} at {signal.entry_price:.5f}, "
                           f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
        
        # Process bearish sweeps (sweep high, reverse down)
        for sweep_data in sweeps['bearish']:
            idx = sweep_data['index']
            
            # Skip if not enough data after sweep
            if idx >= len(data) - 1:
                continue
            
            # Check RSI overbought condition
            if rsi.iloc[idx] < self.rsi_overbought:
                continue
            
            # Check volume spike
            if not volume_spikes.iloc[idx]:
                continue
            
            # Calculate entry, SL, TP
            entry_price = data['close'].iloc[idx]
            stop_loss = data['high'].iloc[idx] + (atr.iloc[idx] * 0.5)
            risk = stop_loss - entry_price
            
            # Ensure minimum risk/reward
            take_profit = entry_price - (risk * self.min_risk_reward)
            risk_reward = (entry_price - take_profit) / risk if risk > 0 else 0
            
            if risk_reward < self.min_risk_reward:
                continue
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                rsi_value=100 - rsi.iloc[idx],  # Invert for bearish
                volume_spike_factor=data['volume'].iloc[idx] / data['volume'].rolling(20).mean().iloc[idx],
                sweep_strength=sweep_data['reversal_strength'],
                zone_strength=sweep_data['zone'].strength
            )
            
            # Create signal
            signal = TrapReversalSignal(
                timestamp=data.index[idx],
                direction='SHORT',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                risk_reward=risk_reward,
                trap_type='liquidity_sweep_high',
                volume_spike_factor=data['volume'].iloc[idx] / data['volume'].rolling(20).mean().iloc[idx],
                rsi_value=rsi.iloc[idx],
                atr_value=atr.iloc[idx]
            )
            
            signals.append(signal)
            self.logger.info(f"Bearish trap signal: {signal.direction} at {signal.entry_price:.5f}, "
                           f"RR={signal.risk_reward:.2f}, Conf={signal.confidence:.2f}")
        
        return signals
    
    def _calculate_confidence(self, rsi_value: float, volume_spike_factor: float,
                             sweep_strength: float, zone_strength: float) -> float:
        """
        Calculate signal confidence (0-1)
        
        Weights:
        - RSI extremity: 30%
        - Volume spike: 25%
        - Sweep strength: 25%
        - Zone strength: 20%
        """
        # RSI extremity (0-1, higher is more extreme)
        rsi_score = min(1.0, (30 - min(rsi_value, 100 - rsi_value)) / 30)
        
        # Volume spike (normalize to 0-1)
        volume_score = min(1.0, (volume_spike_factor - 1.0) / 2.0)
        
        # Sweep strength (already 0-1 from pattern detection)
        sweep_score = min(1.0, sweep_strength)
        
        # Zone strength (already 0-1 from zone identification)
        zone_score = zone_strength
        
        # Weighted average
        confidence = (
            rsi_score * 0.30 +
            volume_score * 0.25 +
            sweep_score * 0.25 +
            zone_score * 0.20
        )
        
        return min(1.0, max(0.0, confidence))
    
    def get_parameters(self) -> Dict:
        """Get current strategy parameters"""
        return {
            'name': self.name,
            'atr_period': self.atr_period,
            'rsi_period': self.rsi_period,
            'volume_spike_threshold': self.volume_spike_threshold,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'min_risk_reward': self.min_risk_reward,
            'position_risk_pct': self.position_risk_pct,
            'lookback_bars': self.lookback_bars,
            'liquidity_buffer_atr': self.liquidity_buffer_atr,
            'min_sweep_distance_atr': self.min_sweep_distance_atr,
            'max_sweep_distance_atr': self.max_sweep_distance_atr
        }


# Convenience function for easy integration
def create_trap_reversal_scalper(**kwargs) -> TrapReversalScalper:
    """Create Trap Reversal Scalper with optional parameter overrides"""
    strategy = TrapReversalScalper()
    
    # Override parameters if provided
    for key, value in kwargs.items():
        if hasattr(strategy, key):
            setattr(strategy, key, value)
    
    return strategy
