#!/usr/bin/env python3
"""
RBOTzilla UNI - Price Action Patterns Module
Pattern detection for advanced strategies
PIN: 841921

Provides:
- Fair Value Gap (FVG) detection
- Consolidation pattern detection
- Engulfing candle patterns
- Liquidity zone identification
- Break of Structure (BoS) detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FairValueGap:
    """Fair Value Gap data structure"""
    start_idx: int
    end_idx: int
    gap_size: float
    gap_high: float
    gap_low: float
    direction: str  # 'bullish' or 'bearish'
    filled: bool = False


@dataclass
class LiquidityZone:
    """Liquidity zone data structure"""
    price_level: float
    zone_high: float
    zone_low: float
    zone_type: str  # 'high', 'low', 'internal'
    strength: float  # 0.0-1.0
    touches: int
    last_touch_idx: int


def detect_fair_value_gaps(high: pd.Series, low: pd.Series, 
                           close: pd.Series, min_size_atr: float = 0.5,
                           atr: Optional[pd.Series] = None) -> List[FairValueGap]:
    """
    Detect Fair Value Gaps (FVG) - 3-candle gaps
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        min_size_atr: Minimum gap size as ATR multiplier
        atr: ATR series (calculated if not provided)
        
    Returns:
        List of FairValueGap objects
    """
    fvgs = []
    
    # Calculate ATR if not provided
    if atr is None:
        from .indicators import calculate_atr
        atr = calculate_atr(high, low, close)
    
    # Check each set of 3 consecutive candles
    for i in range(2, len(high)):
        # Bullish FVG: low[i] > high[i-2]
        if low.iloc[i] > high.iloc[i - 2]:
            gap_size = low.iloc[i] - high.iloc[i - 2]
            
            # Check minimum gap size
            if gap_size >= (atr.iloc[i] * min_size_atr):
                fvg = FairValueGap(
                    start_idx=i - 2,
                    end_idx=i,
                    gap_size=gap_size,
                    gap_high=low.iloc[i],
                    gap_low=high.iloc[i - 2],
                    direction='bullish'
                )
                fvgs.append(fvg)
        
        # Bearish FVG: high[i] < low[i-2]
        elif high.iloc[i] < low.iloc[i - 2]:
            gap_size = low.iloc[i - 2] - high.iloc[i]
            
            # Check minimum gap size
            if gap_size >= (atr.iloc[i] * min_size_atr):
                fvg = FairValueGap(
                    start_idx=i - 2,
                    end_idx=i,
                    gap_size=gap_size,
                    gap_high=low.iloc[i - 2],
                    gap_low=high.iloc[i],
                    direction='bearish'
                )
                fvgs.append(fvg)
    
    return fvgs


def detect_consolidation(high: pd.Series, low: pd.Series, close: pd.Series,
                        period: int = 10, max_range_pct: float = 0.005) -> pd.Series:
    """
    Detect consolidation patterns (tight range)
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Consolidation period (default: 10 bars)
        max_range_pct: Maximum range as percentage (default: 0.5%)
        
    Returns:
        Boolean series indicating consolidation periods
    """
    # Calculate rolling high and low
    rolling_high = high.rolling(window=period).max()
    rolling_low = low.rolling(window=period).min()
    
    # Calculate range percentage
    range_pct = (rolling_high - rolling_low) / close
    
    # Consolidation when range is tight
    return range_pct <= max_range_pct


def detect_engulfing_patterns(open_: pd.Series, high: pd.Series, 
                              low: pd.Series, close: pd.Series,
                              min_body_atr: float = 0.1,
                              atr: Optional[pd.Series] = None) -> Dict[str, pd.Series]:
    """
    Detect bullish and bearish engulfing patterns
    
    Args:
        open_: Open price series
        high: High price series
        low: Low price series
        close: Close price series
        min_body_atr: Minimum engulfing body size as ATR multiplier
        atr: ATR series (calculated if not provided)
        
    Returns:
        Dictionary with 'bullish' and 'bearish' boolean series
    """
    # Calculate ATR if not provided
    if atr is None:
        from .indicators import calculate_atr
        atr = calculate_atr(high, low, close)
    
    # Calculate candle bodies
    body_current = abs(close - open_)
    body_previous = abs(close.shift(1) - open_.shift(1))
    
    # Bullish engulfing: 
    # - Previous candle is bearish (close < open)
    # - Current candle is bullish (close > open)
    # - Current body engulfs previous body
    # - Low of current <= low of previous
    # - Close of current > open of previous
    bullish = (
        (close.shift(1) < open_.shift(1)) &  # Previous bearish
        (close > open_) &  # Current bullish
        (low <= low.shift(1)) &  # Lower low or equal
        (close > open_.shift(1)) &  # Higher close
        (body_current >= min_body_atr * atr)  # Minimum size
    )
    
    # Bearish engulfing:
    # - Previous candle is bullish (close > open)
    # - Current candle is bearish (close < open)
    # - Current body engulfs previous body
    # - High of current >= high of previous
    # - Close of current < open of previous
    bearish = (
        (close.shift(1) > open_.shift(1)) &  # Previous bullish
        (close < open_) &  # Current bearish
        (high >= high.shift(1)) &  # Higher high or equal
        (close < open_.shift(1)) &  # Lower close
        (body_current >= min_body_atr * atr)  # Minimum size
    )
    
    return {
        'bullish': bullish,
        'bearish': bearish
    }


def identify_liquidity_zones(high: pd.Series, low: pd.Series, 
                             lookback: int = 100,
                             buffer_atr: float = 0.2,
                             atr: Optional[pd.Series] = None) -> List[LiquidityZone]:
    """
    Identify liquidity zones (swing highs/lows)
    
    Args:
        high: High price series
        low: Low price series
        lookback: Lookback period for swing identification
        buffer_atr: Zone buffer as ATR multiplier
        atr: ATR series (calculated if not provided)
        
    Returns:
        List of LiquidityZone objects
    """
    zones = []
    
    # Calculate ATR if not provided
    if atr is None:
        from .indicators import calculate_atr, calculate_sma
        # Use close as approximation for ATR calculation
        close = (high + low) / 2
        atr = calculate_atr(high, low, close)
    
    # Find swing highs
    for i in range(lookback, len(high) - lookback):
        window_high = high.iloc[i - lookback:i + lookback + 1]
        
        if high.iloc[i] == window_high.max():
            # Count touches
            touches = sum((high.iloc[i - lookback:i + lookback + 1] >= 
                          high.iloc[i] - buffer_atr * atr.iloc[i]) &
                         (high.iloc[i - lookback:i + lookback + 1] <= 
                          high.iloc[i] + buffer_atr * atr.iloc[i]))
            
            zone = LiquidityZone(
                price_level=high.iloc[i],
                zone_high=high.iloc[i] + buffer_atr * atr.iloc[i],
                zone_low=high.iloc[i] - buffer_atr * atr.iloc[i],
                zone_type='high',
                strength=min(1.0, touches / 5.0),  # Normalize to 0-1
                touches=touches,
                last_touch_idx=i
            )
            zones.append(zone)
    
    # Find swing lows
    for i in range(lookback, len(low) - lookback):
        window_low = low.iloc[i - lookback:i + lookback + 1]
        
        if low.iloc[i] == window_low.min():
            # Count touches
            touches = sum((low.iloc[i - lookback:i + lookback + 1] >= 
                          low.iloc[i] - buffer_atr * atr.iloc[i]) &
                         (low.iloc[i - lookback:i + lookback + 1] <= 
                          low.iloc[i] + buffer_atr * atr.iloc[i]))
            
            zone = LiquidityZone(
                price_level=low.iloc[i],
                zone_high=low.iloc[i] + buffer_atr * atr.iloc[i],
                zone_low=low.iloc[i] - buffer_atr * atr.iloc[i],
                zone_type='low',
                strength=min(1.0, touches / 5.0),  # Normalize to 0-1
                touches=touches,
                last_touch_idx=i
            )
            zones.append(zone)
    
    return zones


def detect_break_of_structure(high: pd.Series, low: pd.Series, close: pd.Series,
                              confirmation_bars: int = 3) -> Dict[str, pd.Series]:
    """
    Detect Break of Structure (BoS)
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        confirmation_bars: Number of bars for confirmation
        
    Returns:
        Dictionary with 'bullish_bos' and 'bearish_bos' boolean series
    """
    # Calculate swing highs and lows
    from .indicators import identify_swing_points
    swing_highs, swing_lows = identify_swing_points(high, low)
    
    # Bullish BoS: Price breaks above previous swing high
    prev_swing_high = high.where(swing_highs).ffill()
    bullish_bos = close > prev_swing_high.shift(1)
    
    # Require confirmation (multiple bars above)
    if confirmation_bars > 1:
        bullish_confirmed = bullish_bos.rolling(window=confirmation_bars).sum() >= confirmation_bars
        bullish_bos = bullish_bos & bullish_confirmed
    
    # Bearish BoS: Price breaks below previous swing low
    prev_swing_low = low.where(swing_lows).ffill()
    bearish_bos = close < prev_swing_low.shift(1)
    
    # Require confirmation (multiple bars below)
    if confirmation_bars > 1:
        bearish_confirmed = bearish_bos.rolling(window=confirmation_bars).sum() >= confirmation_bars
        bearish_bos = bearish_bos & bearish_confirmed
    
    return {
        'bullish_bos': bullish_bos,
        'bearish_bos': bearish_bos
    }


def detect_liquidity_sweep(high: pd.Series, low: pd.Series, close: pd.Series,
                           zones: List[LiquidityZone],
                           min_distance_atr: float = 0.3,
                           max_distance_atr: float = 2.0,
                           atr: Optional[pd.Series] = None) -> Dict[str, List]:
    """
    Detect liquidity sweeps through identified zones
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        zones: List of LiquidityZone objects
        min_distance_atr: Minimum sweep distance as ATR multiplier
        max_distance_atr: Maximum sweep distance as ATR multiplier
        atr: ATR series
        
    Returns:
        Dictionary with sweep information
    """
    sweeps = {
        'bullish': [],  # Sweeps below lows then reverses up
        'bearish': []   # Sweeps above highs then reverses down
    }
    
    # Calculate ATR if not provided
    if atr is None:
        from .indicators import calculate_atr
        atr = calculate_atr(high, low, close)
    
    for zone in zones:
        if zone.zone_type == 'low':
            # Check for bullish sweep (goes below zone then reverses)
            for i in range(zone.last_touch_idx + 1, len(low)):
                # Price sweeps below the zone
                if low.iloc[i] < zone.zone_low:
                    sweep_distance = zone.zone_low - low.iloc[i]
                    
                    # Check distance constraints
                    if (min_distance_atr * atr.iloc[i] <= sweep_distance <= 
                        max_distance_atr * atr.iloc[i]):
                        
                        # Check for reversal (close back above zone)
                        if close.iloc[i] > zone.price_level:
                            sweeps['bullish'].append({
                                'index': i,
                                'zone': zone,
                                'sweep_distance': sweep_distance,
                                'reversal_strength': (close.iloc[i] - low.iloc[i]) / atr.iloc[i]
                            })
                            break
        
        elif zone.zone_type == 'high':
            # Check for bearish sweep (goes above zone then reverses)
            for i in range(zone.last_touch_idx + 1, len(high)):
                # Price sweeps above the zone
                if high.iloc[i] > zone.zone_high:
                    sweep_distance = high.iloc[i] - zone.zone_high
                    
                    # Check distance constraints
                    if (min_distance_atr * atr.iloc[i] <= sweep_distance <= 
                        max_distance_atr * atr.iloc[i]):
                        
                        # Check for reversal (close back below zone)
                        if close.iloc[i] < zone.price_level:
                            sweeps['bearish'].append({
                                'index': i,
                                'zone': zone,
                                'sweep_distance': sweep_distance,
                                'reversal_strength': (high.iloc[i] - close.iloc[i]) / atr.iloc[i]
                            })
                            break
    
    return sweeps


def calculate_pattern_strength(pattern_signals: pd.Series, 
                               volume: pd.Series,
                               volume_threshold: float = 1.5) -> pd.Series:
    """
    Calculate pattern strength based on volume confirmation
    
    Args:
        pattern_signals: Boolean series of pattern detections
        volume: Volume series
        volume_threshold: Volume spike threshold
        
    Returns:
        Pattern strength (0.0-1.0)
    """
    from .indicators import calculate_volume_spike
    
    # Detect volume spikes
    volume_spikes = calculate_volume_spike(volume, threshold=volume_threshold)
    
    # Combine pattern with volume
    strength = pd.Series(0.0, index=pattern_signals.index)
    strength[pattern_signals & volume_spikes] = 1.0
    strength[pattern_signals & ~volume_spikes] = 0.6
    
    return strength
