#!/usr/bin/env python3
"""
RBOTzilla UNI - Regime Features Module
Market regime detection and classification
PIN: 841921

Provides:
- Trend regime detection (Bullish/Bearish/Sideways)
- Volatility regime classification
- Volume regime analysis
- Market structure analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from enum import Enum


class TrendRegime(Enum):
    """Trend regime classification"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"
    UNDEFINED = "UNDEFINED"


class VolatilityRegime(Enum):
    """Volatility regime classification"""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


def detect_trend_regime(close: pd.Series, 
                       fast_period: int = 50,
                       slow_period: int = 200,
                       sideways_threshold: float = 0.001) -> pd.Series:
    """
    Detect trend regime using EMA analysis
    
    Args:
        close: Close price series
        fast_period: Fast EMA period (default: 50)
        slow_period: Slow EMA period (default: 200)
        sideways_threshold: Threshold for sideways market (0.1%)
        
    Returns:
        Series with trend regime labels
    """
    from .indicators import calculate_ema
    
    ema_fast = calculate_ema(close, fast_period)
    ema_slow = calculate_ema(close, slow_period)
    
    # Calculate EMA separation percentage
    separation = (ema_fast - ema_slow) / ema_slow
    
    # Classify regime
    regime = pd.Series(TrendRegime.UNDEFINED.value, index=close.index)
    
    regime[separation > sideways_threshold] = TrendRegime.BULLISH.value
    regime[separation < -sideways_threshold] = TrendRegime.BEARISH.value
    regime[abs(separation) <= sideways_threshold] = TrendRegime.SIDEWAYS.value
    
    return regime


def detect_volatility_regime(high: pd.Series, low: pd.Series, 
                             close: pd.Series, period: int = 14,
                             percentiles: Tuple[float, float, float] = (25, 75, 95)) -> pd.Series:
    """
    Detect volatility regime using ATR percentiles
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: ATR period (default: 14)
        percentiles: Tuple of (low, normal, high) percentile thresholds
        
    Returns:
        Series with volatility regime labels
    """
    from .indicators import calculate_atr
    
    atr = calculate_atr(high, low, close, period)
    
    # Calculate rolling percentiles
    lookback = max(100, period * 5)
    p_low = atr.rolling(window=lookback).quantile(percentiles[0] / 100)
    p_high = atr.rolling(window=lookback).quantile(percentiles[1] / 100)
    p_extreme = atr.rolling(window=lookback).quantile(percentiles[2] / 100)
    
    # Classify regime
    regime = pd.Series(VolatilityRegime.NORMAL.value, index=close.index)
    
    regime[atr <= p_low] = VolatilityRegime.LOW.value
    regime[atr > p_high] = VolatilityRegime.HIGH.value
    regime[atr > p_extreme] = VolatilityRegime.EXTREME.value
    
    return regime


def calculate_market_structure(high: pd.Series, low: pd.Series, 
                               close: pd.Series,
                               lookback: int = 50) -> Dict[str, pd.Series]:
    """
    Calculate market structure features
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        lookback: Lookback period
        
    Returns:
        Dictionary with market structure indicators
    """
    # Higher highs and higher lows (bullish structure)
    rolling_high = high.rolling(window=lookback).max()
    rolling_low = low.rolling(window=lookback).min()
    
    higher_highs = high > rolling_high.shift(lookback)
    higher_lows = low > rolling_low.shift(lookback)
    
    # Lower highs and lower lows (bearish structure)
    lower_highs = high < rolling_high.shift(lookback)
    lower_lows = low < rolling_low.shift(lookback)
    
    # Structure strength (0-1)
    bullish_structure = (higher_highs.astype(int) + higher_lows.astype(int)) / 2
    bearish_structure = (lower_highs.astype(int) + lower_lows.astype(int)) / 2
    
    return {
        'higher_highs': higher_highs,
        'higher_lows': higher_lows,
        'lower_highs': lower_highs,
        'lower_lows': lower_lows,
        'bullish_structure': bullish_structure,
        'bearish_structure': bearish_structure
    }


def calculate_regime_strength(close: pd.Series, volume: pd.Series,
                              regime: pd.Series) -> pd.Series:
    """
    Calculate regime strength (confidence in current regime)
    
    Args:
        close: Close price series
        volume: Volume series
        regime: Trend regime series
        
    Returns:
        Regime strength (0-1)
    """
    from .indicators import calculate_price_momentum, calculate_sma
    
    # Calculate momentum
    momentum = calculate_price_momentum(close, period=10)
    
    # Calculate volume trend
    volume_ma = calculate_sma(volume, 20)
    volume_trend = volume / volume_ma
    
    # Initialize strength
    strength = pd.Series(0.5, index=close.index)
    
    # Adjust strength based on momentum and volume
    for i in range(len(regime)):
        if regime.iloc[i] == TrendRegime.BULLISH.value:
            # Bullish regime: strong if positive momentum and volume
            momentum_factor = min(1.0, max(0.0, (momentum.iloc[i] + 5) / 10))
            volume_factor = min(1.0, volume_trend.iloc[i])
            strength.iloc[i] = (momentum_factor + volume_factor) / 2
            
        elif regime.iloc[i] == TrendRegime.BEARISH.value:
            # Bearish regime: strong if negative momentum and volume
            momentum_factor = min(1.0, max(0.0, (-momentum.iloc[i] + 5) / 10))
            volume_factor = min(1.0, volume_trend.iloc[i])
            strength.iloc[i] = (momentum_factor + volume_factor) / 2
            
        elif regime.iloc[i] == TrendRegime.SIDEWAYS.value:
            # Sideways regime: strong if low momentum
            strength.iloc[i] = 1.0 - min(1.0, abs(momentum.iloc[i]) / 5)
    
    return strength


def detect_regime_change(regime: pd.Series, min_duration: int = 5) -> pd.Series:
    """
    Detect regime changes with minimum duration filter
    
    Args:
        regime: Trend regime series
        min_duration: Minimum bars for regime confirmation
        
    Returns:
        Boolean series indicating regime changes
    """
    # Detect when regime changes
    regime_changed = regime != regime.shift(1)
    
    # Filter short-lived changes
    regime_confirmed = regime.copy()
    
    for i in range(min_duration, len(regime)):
        # Check if regime has been stable for min_duration
        recent_regime = regime.iloc[i - min_duration:i + 1]
        if len(recent_regime.unique()) == 1:
            regime_confirmed.iloc[i] = regime.iloc[i]
        else:
            regime_confirmed.iloc[i] = regime_confirmed.iloc[i - 1]
    
    # Detect confirmed changes
    confirmed_changes = regime_confirmed != regime_confirmed.shift(1)
    
    return confirmed_changes


def calculate_trend_quality(close: pd.Series, high: pd.Series, low: pd.Series,
                            period: int = 20) -> pd.Series:
    """
    Calculate trend quality score (0-1)
    Higher score = cleaner, stronger trend
    
    Args:
        close: Close price series
        high: High price series
        low: Low price series
        period: Analysis period
        
    Returns:
        Trend quality score
    """
    from .indicators import calculate_sma, calculate_atr
    
    # Calculate trend line (SMA)
    sma = calculate_sma(close, period)
    
    # Calculate price distance from trend
    price_deviation = abs(close - sma) / sma
    
    # Calculate ATR for normalization
    atr = calculate_atr(high, low, close, period)
    atr_pct = atr / close
    
    # Quality score (inverse of deviation, normalized by volatility)
    quality = 1.0 - (price_deviation / (atr_pct + 0.001))
    quality = quality.clip(0, 1)
    
    return quality


def identify_consolidation_breakout(high: pd.Series, low: pd.Series,
                                   close: pd.Series, volume: pd.Series,
                                   consol_period: int = 10,
                                   breakout_threshold: float = 1.5) -> Dict[str, pd.Series]:
    """
    Identify consolidation and breakout events
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        volume: Volume series
        consol_period: Consolidation detection period
        breakout_threshold: Volume threshold for breakout confirmation
        
    Returns:
        Dictionary with consolidation and breakout indicators
    """
    from .patterns import detect_consolidation
    from .indicators import calculate_volume_spike, calculate_atr
    
    # Detect consolidation
    is_consolidating = detect_consolidation(high, low, close, period=consol_period)
    
    # Detect volume breakout
    volume_spike = calculate_volume_spike(volume, threshold=breakout_threshold)
    
    # Calculate ATR for breakout measurement
    atr = calculate_atr(high, low, close)
    
    # Bullish breakout: price breaks above consolidation high with volume
    consol_high = high.rolling(window=consol_period).max()
    bullish_breakout = (close > consol_high.shift(1)) & volume_spike & is_consolidating.shift(1)
    
    # Bearish breakout: price breaks below consolidation low with volume
    consol_low = low.rolling(window=consol_period).min()
    bearish_breakout = (close < consol_low.shift(1)) & volume_spike & is_consolidating.shift(1)
    
    return {
        'is_consolidating': is_consolidating,
        'bullish_breakout': bullish_breakout,
        'bearish_breakout': bearish_breakout,
        'consol_high': consol_high,
        'consol_low': consol_low
    }


def calculate_regime_features(high: pd.Series, low: pd.Series, 
                              close: pd.Series, volume: pd.Series) -> Dict[str, pd.Series]:
    """
    Calculate comprehensive regime features for strategy filtering
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        volume: Volume series
        
    Returns:
        Dictionary with all regime features
    """
    # Detect regimes
    trend_regime = detect_trend_regime(close)
    volatility_regime = detect_volatility_regime(high, low, close)
    
    # Calculate market structure
    structure = calculate_market_structure(high, low, close)
    
    # Calculate regime strength
    regime_strength = calculate_regime_strength(close, volume, trend_regime)
    
    # Calculate trend quality
    trend_quality = calculate_trend_quality(close, high, low)
    
    # Detect regime changes
    regime_changes = detect_regime_change(trend_regime)
    
    # Consolidation and breakout
    breakout_info = identify_consolidation_breakout(high, low, close, volume)
    
    # Combine all features
    features = {
        'trend_regime': trend_regime,
        'volatility_regime': volatility_regime,
        'regime_strength': regime_strength,
        'trend_quality': trend_quality,
        'regime_changed': regime_changes,
        **structure,
        **breakout_info
    }
    
    return features


def filter_by_regime(signals: pd.Series, regime: pd.Series, 
                     allowed_regimes: list) -> pd.Series:
    """
    Filter signals by allowed regimes
    
    Args:
        signals: Boolean signal series
        regime: Regime classification series
        allowed_regimes: List of allowed regime values
        
    Returns:
        Filtered signals
    """
    regime_filter = regime.isin(allowed_regimes)
    return signals & regime_filter
