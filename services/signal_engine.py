#!/usr/bin/env python3
"""
Cross-Market Signal Engine - RBOTzilla Multi-Broker Phase 3
Shared intelligence layer for Coinbase and OANDA execution adapters.

Computes:
  - BTC momentum (rolling EMAs)
  - Gold momentum (GC=F via Yahoo Finance)
  - DXY trend (UUP ETF as proxy)
  - Rolling BTC/Gold correlation
  - Macro-event risk flag (scheduled economic events)
  - Composite confidence score (0-100)

PIN: 841921
"""

from __future__ import annotations

import logging
import os
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class MarketSnapshot:
    """Normalized price snapshot for a single instrument."""
    symbol: str
    price: float
    timestamp: str
    source: str = "unknown"


@dataclass
class CrossMarketSignal:
    """Output of one signal engine evaluation cycle."""
    timestamp: str
    btc_momentum: float          # positive = bullish, negative = bearish  [-1, 1]
    gold_momentum: float         # same scale
    dxy_trend: float             # positive = USD strengthening
    btc_gold_correlation: float  # rolling correlation [-1, 1]
    macro_risk_flag: bool        # True when a major event is imminent
    confidence_score: float      # 0-100 composite confidence
    regime: str                  # "RISK_ON" | "RISK_OFF" | "NEUTRAL"
    raw: Dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Price source (thin wrapper - avoids heavy imports if libraries missing)
# ---------------------------------------------------------------------------

class _PriceFetcher:
    """
    Thin price fetcher that tries the repo's free_market_data connector
    first, then falls back to direct Yahoo Finance requests.
    """

    def __init__(self):
        self._session = None
        self._free_md = None
        try:
            from connectors.free_market_data import FreeMarketDataConnector
            self._free_md = FreeMarketDataConnector()
            logger.debug("Using FreeMarketDataConnector for price data.")
        except Exception:
            import requests
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "Mozilla/5.0 RickSignalEngine/1.0"
            })
            logger.debug("FreeMarketDataConnector unavailable; using direct requests to Yahoo Finance.")

    # Map from internal symbol to Yahoo ticker
    _YAHOO_MAP: Dict[str, str] = {
        "BTC.USD":  "BTC-USD",
        "GOLD":     "GC=F",
        "DXY":      "UUP",       # DXY ETF proxy (Invesco DB US Dollar Index Bullish)
        "NASDAQ":   "QQQ",
        "VIX":      "^VIX",
    }

    def fetch(self, symbol: str) -> Optional[float]:
        """Return the current price for *symbol* or None on failure."""
        if self._free_md is not None:
            try:
                result = self._free_md.get_current_price(symbol)
                if result and result.get("price"):
                    return float(result["price"])
            except Exception as exc:
                logger.debug("FreeMarketDataConnector error for %s: %s", symbol, exc)

        # Fallback: direct Yahoo Finance
        yahoo_sym = self._YAHOO_MAP.get(symbol, symbol)
        return self._yahoo_source(yahoo_sym)

    def _yahoo_source(self, yahoo_symbol: str) -> Optional[float]:
        import requests as _req

        session = self._session or _req.Session()
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
        try:
            resp = session.get(url, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            result = data.get("chart", {}).get("result", [])
            if result:
                price = result[0]["meta"].get("regularMarketPrice")
                if price:
                    return float(price)
        except Exception as exc:
            logger.debug("Yahoo Finance request failed for %s: %s", yahoo_symbol, exc)
        return None


# ---------------------------------------------------------------------------
# Rolling helpers
# ---------------------------------------------------------------------------

def _ema(prices: List[float], span: int) -> float:
    """Compute the final EMA value for a price series."""
    if not prices:
        return 0.0
    k = 2.0 / (span + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema


def _momentum(prices: List[float], fast: int = 9, slow: int = 21) -> float:
    """
    Normalised momentum: (fast_ema - slow_ema) / slow_ema, clamped to [-1, 1].
    Returns 0.0 when insufficient data.
    """
    if len(prices) < slow:
        return 0.0
    fast_e = _ema(prices[-fast:], fast)
    slow_e = _ema(prices[-slow:], slow)
    if slow_e == 0:
        return 0.0
    raw = (fast_e - slow_e) / slow_e
    return max(-1.0, min(1.0, raw * 100))


def _rolling_correlation(xs: List[float], ys: List[float], window: int = 30) -> float:
    """
    Pearson correlation of the last *window* samples from two series.
    Returns 0.0 when data is insufficient or std-dev is zero.
    """
    n = min(len(xs), len(ys), window)
    if n < 5:
        return 0.0
    xw = xs[-n:]
    yw = ys[-n:]
    try:
        mean_x = sum(xw) / n
        mean_y = sum(yw) / n
        cov = sum((a - mean_x) * (b - mean_y) for a, b in zip(xw, yw)) / n
        std_x = (sum((a - mean_x) ** 2 for a in xw) / n) ** 0.5
        std_y = (sum((b - mean_y) ** 2 for b in yw) / n) ** 0.5
        if std_x == 0 or std_y == 0:
            return 0.0
        return max(-1.0, min(1.0, cov / (std_x * std_y)))
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

class SignalEngine:
    """
    Cross-market signal engine.  Maintains rolling price histories and
    emits a CrossMarketSignal on each call to evaluate().

    Usage::

        engine = SignalEngine(pin=841921)
        signal = engine.evaluate()
        print(signal.confidence_score, signal.regime)
    """

    BUFFER_SIZE = 200  # keep last N samples per symbol

    def __init__(self, pin: int = 841921, history_size: int = BUFFER_SIZE):
        self._validate_pin(pin)
        self._fetcher = _PriceFetcher()
        self._history: Dict[str, Deque[float]] = {
            sym: deque(maxlen=history_size)
            for sym in ("BTC.USD", "GOLD", "DXY")
        }
        self._last_eval: Optional[CrossMarketSignal] = None
        logger.info("SignalEngine initialised (history_size=%d).", history_size)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, symbol: str, price: float) -> None:
        """
        Push a new price observation into the rolling history.
        Useful when external code feeds prices rather than fetching live.
        """
        if symbol in self._history:
            self._history[symbol].append(price)

    def evaluate(self) -> CrossMarketSignal:
        """
        Fetch current prices, update histories, and compute the full signal.
        Returns a CrossMarketSignal dataclass.
        """
        # 1. Fetch latest prices
        raw: Dict[str, Optional[float]] = {}
        for sym in ("BTC.USD", "GOLD", "DXY"):
            try:
                price = self._fetcher.fetch(sym)
            except Exception as exc:
                logger.debug("Price fetch failed for %s: %s", sym, exc)
                price = None
            raw[sym] = price
            if price is not None:
                self._history[sym].append(price)

        # 2. Compute individual signals
        btc_hist  = list(self._history["BTC.USD"])
        gold_hist = list(self._history["GOLD"])
        dxy_hist  = list(self._history["DXY"])

        btc_mom   = _momentum(btc_hist)
        gold_mom  = _momentum(gold_hist)
        dxy_trend = _momentum(dxy_hist)
        btc_gold_corr = _rolling_correlation(btc_hist, gold_hist)

        # 3. Macro risk flag (placeholder — extend with real calendar integration)
        macro_flag = self._check_macro_risk()

        # 4. Composite confidence score
        confidence = self._compute_confidence(
            btc_mom, gold_mom, dxy_trend, btc_gold_corr, macro_flag
        )

        # 5. Regime classification
        regime = self._classify_regime(btc_mom, gold_mom, dxy_trend, macro_flag)

        signal = CrossMarketSignal(
            timestamp=datetime.now(timezone.utc).isoformat(),
            btc_momentum=btc_mom,
            gold_momentum=gold_mom,
            dxy_trend=dxy_trend,
            btc_gold_correlation=btc_gold_corr,
            macro_risk_flag=macro_flag,
            confidence_score=confidence,
            regime=regime,
            raw=raw,
        )
        self._last_eval = signal
        return signal

    def last_signal(self) -> Optional[CrossMarketSignal]:
        """Return the most recent evaluated signal, or None if evaluate() hasn't run."""
        return self._last_eval

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_pin(pin: int) -> None:
        """Charter PIN guard (mirrors foundation.rick_charter logic)."""
        try:
            from foundation.rick_charter import validate_pin as _vp
            _vp(pin)
        except ImportError:
            if pin != 841921:
                raise ValueError(f"Invalid PIN: {pin}")

    @staticmethod
    def _check_macro_risk() -> bool:
        """
        Lightweight macro event check.
        In production this should be replaced with a real economic calendar
        feed (e.g., Forex Factory API, broker calendar endpoint).
        Returns True when within 30 minutes of a known high-impact window.
        """
        now = datetime.now(timezone.utc)
        # High-impact windows: US Non-Farm Payrolls (first Friday), FOMC minutes
        # Simplified heuristic: flag Fridays 13:25-14:15 UTC (NFP window)
        if now.weekday() == 4 and 13 <= now.hour <= 14:
            return True
        return False

    @staticmethod
    def _compute_confidence(
        btc_mom: float,
        gold_mom: float,
        dxy_trend: float,
        btc_gold_corr: float,
        macro_flag: bool,
    ) -> float:
        """
        Blend individual signals into a 0-100 confidence score.

        Weights:
          40% BTC momentum magnitude
          25% Gold momentum magnitude
          15% DXY trend magnitude
          20% cross-market correlation clarity (|corr| > 0.5 is good)
          Penalty: -25 points when macro risk flag is active
        """
        btc_score  = abs(btc_mom)  * 40
        gold_score = abs(gold_mom) * 25
        dxy_score  = abs(dxy_trend) * 15
        corr_score = (abs(btc_gold_corr) - 0.3) / 0.7 * 20 if abs(btc_gold_corr) > 0.3 else 0.0

        raw_score = btc_score + gold_score + dxy_score + max(0.0, corr_score)
        if macro_flag:
            raw_score -= 25.0

        return round(max(0.0, min(100.0, raw_score)), 2)

    @staticmethod
    def _classify_regime(
        btc_mom: float,
        gold_mom: float,
        dxy_trend: float,
        macro_flag: bool,
    ) -> str:
        """
        Classify macro regime.
          RISK_ON  : BTC bullish, gold flat/down, USD flat/down
          RISK_OFF : gold bullish, BTC weak/negative, USD strong OR macro flag
          NEUTRAL  : mixed / low-conviction signals
        """
        if macro_flag:
            return "RISK_OFF"

        risk_on_score  = (1 if btc_mom > 0.05 else 0) + (1 if gold_mom < 0 else 0) + (1 if dxy_trend < 0 else 0)
        risk_off_score = (1 if gold_mom > 0.05 else 0) + (1 if btc_mom < 0 else 0) + (1 if dxy_trend > 0.05 else 0)

        if risk_on_score >= 2:
            return "RISK_ON"
        if risk_off_score >= 2:
            return "RISK_OFF"
        return "NEUTRAL"
