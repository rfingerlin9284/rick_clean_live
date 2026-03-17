"""
signals/features.py – cross-market feature generation.

Each function receives a pandas DataFrame with columns
[open, high, low, close, volume] and returns a scalar feature value.
"""

from __future__ import annotations

import pandas as pd


def momentum(close: pd.Series, window: int = 14) -> float:
    """Rate-of-change momentum over *window* periods (0.0 = flat)."""
    if len(close) < window + 1:
        return 0.0
    return float((close.iloc[-1] / close.iloc[-window - 1]) - 1.0)


def rolling_correlation(series_a: pd.Series, series_b: pd.Series, window: int = 20) -> float:
    """Rolling Pearson correlation between two return series."""
    min_len = min(len(series_a), len(series_b))
    if min_len < window:
        return 0.0
    ret_a = series_a.pct_change().dropna()
    ret_b = series_b.pct_change().dropna()
    aligned = pd.concat([ret_a, ret_b], axis=1).dropna()
    if len(aligned) < window:
        return 0.0
    return float(aligned.iloc[:, 0].rolling(window).corr(aligned.iloc[:, 1]).iloc[-1])


def simple_moving_average(close: pd.Series, window: int = 20) -> float:
    """Simple moving average of the last *window* closes."""
    if len(close) < window:
        return float(close.mean())
    return float(close.rolling(window).mean().iloc[-1])


def trend_direction(close: pd.Series, fast: int = 10, slow: int = 30) -> float:
    """Returns +1.0 (uptrend), -1.0 (downtrend), or 0.0 (neutral) based on SMA crossover."""
    if len(close) < slow:
        return 0.0
    fast_sma = simple_moving_average(close, fast)
    slow_sma = simple_moving_average(close, slow)
    if fast_sma > slow_sma:
        return 1.0
    if fast_sma < slow_sma:
        return -1.0
    return 0.0
