#!/usr/bin/env python3
"""
RBOTzilla UNI - Technical Indicators Module
Shared technical indicators for all strategies
PIN: 841921

Provides:
- RSI (Relative Strength Index)
- ATR (Average True Range)
- Bollinger Bands
- MACD (Moving Average Convergence Divergence)
- EMAs (Exponential Moving Averages)
- Volume analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index
    
    Args:
        prices: Price series (typically close prices)
        period: RSI period (default: 14)
        
    Returns:
        RSI values (0-100)
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 14) -> pd.Series:
    """
    Calculate Average True Range
    
    Args:
        high: High price series
        low: Low price series  
        close: Close price series
        period: ATR period (default: 14)
        
    Returns:
        ATR values
    """
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, 
                               std_dev: float = 2.0) -> Dict[str, pd.Series]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: Price series (typically close prices)
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        
    Returns:
        Dictionary with 'upper', 'middle', 'lower' bands
    """
    sma = prices.rolling(window=period).mean()
    rolling_std = prices.rolling(window=period).std()
    
    return {
        'upper': sma + (rolling_std * std_dev),
        'middle': sma,
        'lower': sma - (rolling_std * std_dev),
        'std': rolling_std
    }


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, 
                   signal: int = 9) -> Dict[str, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: Price series (typically close prices)
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
        
    Returns:
        Dictionary with 'macd', 'signal', 'histogram'
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average
    
    Args:
        prices: Price series
        period: EMA period
        
    Returns:
        EMA values
    """
    return prices.ewm(span=period, adjust=False).mean()


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average
    
    Args:
        prices: Price series
        period: SMA period
        
    Returns:
        SMA values
    """
    return prices.rolling(window=period).mean()


def calculate_volume_spike(volume: pd.Series, period: int = 20, 
                           threshold: float = 1.5) -> pd.Series:
    """
    Detect volume spikes
    
    Args:
        volume: Volume series
        period: Lookback period for average (default: 20)
        threshold: Spike threshold multiplier (default: 1.5x)
        
    Returns:
        Boolean series indicating volume spikes
    """
    avg_volume = volume.rolling(window=period).mean()
    return volume > (avg_volume * threshold)


def calculate_volatility_ratio(high: pd.Series, low: pd.Series, 
                               close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate volatility ratio using ATR
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period
        
    Returns:
        Volatility ratio (current ATR / historical ATR)
    """
    atr = calculate_atr(high, low, close, period)
    atr_ma = atr.rolling(window=period).mean()
    
    return atr / atr_ma


def identify_swing_points(high: pd.Series, low: pd.Series, 
                         lookback: int = 10) -> Tuple[pd.Series, pd.Series]:
    """
    Identify swing highs and lows
    
    Args:
        high: High price series
        low: Low price series
        lookback: Lookback window for swing identification
        
    Returns:
        Tuple of (swing_highs, swing_lows) series
    """
    swing_highs = high.rolling(window=lookback * 2 + 1, center=True).max() == high
    swing_lows = low.rolling(window=lookback * 2 + 1, center=True).min() == low
    
    return swing_highs, swing_lows


def calculate_price_momentum(close: pd.Series, period: int = 10) -> pd.Series:
    """
    Calculate price momentum (rate of change)
    
    Args:
        close: Close price series
        period: Momentum period
        
    Returns:
        Momentum values (percentage change)
    """
    return (close - close.shift(period)) / close.shift(period) * 100


def calculate_candle_range(high: pd.Series, low: pd.Series, 
                          close: pd.Series) -> Dict[str, pd.Series]:
    """
    Calculate candle range metrics
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        
    Returns:
        Dictionary with range metrics
    """
    range_abs = high - low
    range_pct = range_abs / close * 100
    
    return {
        'range_abs': range_abs,
        'range_pct': range_pct,
        'midpoint': (high + low) / 2
    }


def calculate_trend_strength(close: pd.Series, fast_period: int = 10, 
                             slow_period: int = 50) -> pd.Series:
    """
    Calculate trend strength using EMA separation
    
    Args:
        close: Close price series
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        
    Returns:
        Trend strength (percentage separation)
    """
    ema_fast = calculate_ema(close, fast_period)
    ema_slow = calculate_ema(close, slow_period)
    
    return (ema_fast - ema_slow) / ema_slow * 100


# Utility functions for strategy use
def is_oversold(rsi: pd.Series, threshold: float = 30) -> pd.Series:
    """Check if RSI indicates oversold conditions"""
    return rsi < threshold


def is_overbought(rsi: pd.Series, threshold: float = 70) -> pd.Series:
    """Check if RSI indicates overbought conditions"""
    return rsi > threshold


def is_bullish_crossover(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """Detect bullish crossover (fast crosses above slow)"""
    return (fast > slow) & (fast.shift(1) <= slow.shift(1))


def is_bearish_crossover(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """Detect bearish crossover (fast crosses below slow)"""
    return (fast < slow) & (fast.shift(1) >= slow.shift(1))


def price_above_band(price: pd.Series, band: pd.Series) -> pd.Series:
    """Check if price is above a band/level"""
    return price > band


def price_below_band(price: pd.Series, band: pd.Series) -> pd.Series:
    """Check if price is below a band/level"""
    return price < band
