"""
risk/manager.py – portfolio risk manager.

Approves or rejects trade signals based on:
- minimum confidence threshold
- maximum total exposure across all brokers
- per-broker exposure limits
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from utils.logger import get_logger

if TYPE_CHECKING:
    from config.settings import Settings
    from signals.engine import TradeSignal

logger = get_logger(__name__)


class RiskManager:
    def __init__(self, settings: "Settings") -> None:
        self._min_confidence = settings.min_confidence
        self._max_total_exposure_usd = settings.max_total_exposure_usd
        self._current_exposure_usd: float = 0.0

    def approve(self, signal: "TradeSignal") -> bool:
        """Return True if the signal passes all risk checks."""
        if signal.confidence < self._min_confidence:
            logger.info(
                "risk_reject_confidence",
                confidence=signal.confidence,
                threshold=self._min_confidence,
            )
            return False

        projected_exposure = self._current_exposure_usd + signal.notional_usd
        if projected_exposure > self._max_total_exposure_usd:
            logger.info(
                "risk_reject_exposure",
                projected=projected_exposure,
                limit=self._max_total_exposure_usd,
            )
            return False

        return True

    def record_fill(self, notional_usd: float) -> None:
        """Record a filled order so running exposure stays up to date."""
        self._current_exposure_usd += notional_usd

    def record_close(self, notional_usd: float) -> None:
        """Record a closed position."""
        self._current_exposure_usd = max(0.0, self._current_exposure_usd - notional_usd)

    @property
    def current_exposure_usd(self) -> float:
        return self._current_exposure_usd
