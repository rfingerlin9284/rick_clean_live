"""
signals/engine.py – shared signal engine.

Gathers market data from both brokers, computes cross-market features,
scores trade confidence, and returns a list of TradeSignal objects.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

import pandas as pd

from signals import features
from utils.logger import get_logger

if TYPE_CHECKING:
    from config.settings import Settings
    from brokers.coinbase.client import CoinbaseClient
    from brokers.oanda.client import OandaClient

logger = get_logger(__name__)


@dataclass
class TradeSignal:
    broker: str          # "coinbase" | "oanda"
    symbol: str          # e.g. "BTC-USD" or "EUR_USD"
    side: str            # "buy" | "sell"
    confidence: float    # 0.0 – 1.0
    notional_usd: float  # approximate USD exposure
    units: float = 0.0   # units for OANDA orders
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return (
            f"TradeSignal(broker={self.broker}, symbol={self.symbol}, "
            f"side={self.side}, confidence={self.confidence:.2f}, "
            f"notional_usd={self.notional_usd:.2f})"
        )


class SignalEngine:
    """Computes trade signals for Coinbase and OANDA instruments."""

    # Instruments to watch
    COINBASE_INSTRUMENTS = ["BTC-USD", "ETH-USD"]
    OANDA_INSTRUMENTS = ["XAU_USD", "EUR_USD"]

    def __init__(
        self,
        settings: "Settings",
        coinbase: "CoinbaseClient",
        oanda: "OandaClient",
    ) -> None:
        self._settings = settings
        self._coinbase = coinbase
        self._oanda = oanda

    # ------------------------------------------------------------------

    def run(self) -> List[TradeSignal]:
        """Run one full signal cycle and return approved signals."""
        signals: List[TradeSignal] = []

        # --- Coinbase signals ---
        for symbol in self.COINBASE_INSTRUMENTS:
            try:
                candles = self._coinbase.get_candles(symbol, granularity="ONE_HOUR", limit=50)
                close = _candles_to_close(candles, source="coinbase")
                if close.empty:
                    continue
                signal = self._score_coinbase(symbol, close)
                if signal is not None:
                    signals.append(signal)
            except Exception as exc:  # noqa: BLE001
                logger.warning("coinbase_signal_error", symbol=symbol, error=str(exc))

        # --- OANDA signals ---
        for instrument in self.OANDA_INSTRUMENTS:
            try:
                candles = self._oanda.get_candles(instrument, granularity="H1", count=50)
                close = _candles_to_close(candles, source="oanda")
                if close.empty:
                    continue
                signal = self._score_oanda(instrument, close)
                if signal is not None:
                    signals.append(signal)
            except Exception as exc:  # noqa: BLE001
                logger.warning("oanda_signal_error", instrument=instrument, error=str(exc))

        logger.info("signals_generated", count=len(signals))
        return signals

    # ------------------------------------------------------------------
    # Private scoring helpers
    # ------------------------------------------------------------------

    def _score_coinbase(self, symbol: str, close: pd.Series) -> TradeSignal | None:
        mom = features.momentum(close, window=14)
        trend = features.trend_direction(close, fast=10, slow=30)
        confidence = _combine_scores(mom, trend)

        if confidence < self._settings.min_confidence:
            return None

        side = "buy" if trend >= 0 else "sell"
        return TradeSignal(
            broker="coinbase",
            symbol=symbol,
            side=side,
            confidence=confidence,
            notional_usd=min(100.0, self._settings.max_total_exposure_usd * 0.1),
        )

    def _score_oanda(self, instrument: str, close: pd.Series) -> TradeSignal | None:
        mom = features.momentum(close, window=14)
        trend = features.trend_direction(close, fast=10, slow=30)
        confidence = _combine_scores(mom, trend)

        if confidence < self._settings.min_confidence:
            return None

        side = "buy" if trend >= 0 else "sell"
        units = 1000.0  # 1 micro-lot as a safe default
        return TradeSignal(
            broker="oanda",
            symbol=instrument,
            side=side,
            confidence=confidence,
            notional_usd=min(100.0, self._settings.max_total_exposure_usd * 0.1),
            units=units,
        )


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _candles_to_close(candles: list, source: str) -> pd.Series:
    """Convert raw candle dicts to a pandas Series of closing prices."""
    closes: list[float] = []
    for c in candles:
        try:
            if source == "coinbase":
                closes.append(float(c["close"]))
            else:  # oanda
                closes.append(float(c["mid"]["c"]))
        except (KeyError, TypeError, ValueError):
            continue
    return pd.Series(closes, dtype=float)


def _combine_scores(momentum_score: float, trend_score: float) -> float:
    """Combine momentum and trend into a 0–1 confidence score."""
    # Normalize momentum to 0–1 range (cap at ±10 %)
    normalized_mom = max(-1.0, min(1.0, momentum_score / 0.10))
    raw = (normalized_mom + trend_score) / 2.0  # -1 to +1
    return (raw + 1.0) / 2.0  # shift to 0–1
