#!/usr/bin/env python3
"""
Headless Runner - RBOTzilla Multi-Broker Phase 1
Main entrypoint for the headless multi-broker trading system.

Wires together:
  - SignalEngine    (cross-market intelligence)
  - NewsScanner     (background news / confidence scoring)
  - OandaConnector  (OANDA v20 execution)
  - CoinbaseConnector (Coinbase Advanced Trade execution)
  - RickCharter     (immutable safety rules)

Supports PAPER (practice) and LIVE modes controlled by environment:
  MODE=paper   — uses practice API endpoints, no real money at risk
  MODE=live    — requires PIN validation and live API credentials

Usage:
    python headless_runner.py           # paper mode (default)
    MODE=live python headless_runner.py # live mode

PIN: 841921
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Optional

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------
LOG_DIR = REPO_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "headless_runner.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("headless_runner")

# ------------------------------------------------------------------
# Environment loading
# ------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    _env_file = REPO_ROOT / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
        logger.info("Loaded .env from %s", _env_file)
except ImportError:
    pass  # python-dotenv not installed; rely on shell env


# ------------------------------------------------------------------
# Charter & shared components
# ------------------------------------------------------------------
def _load_charter(pin: int):
    try:
        from foundation.rick_charter import RickCharter
        charter = RickCharter()
        charter.validate_pin(pin)
        return charter
    except Exception as exc:
        logger.warning("RickCharter not available: %s", exc)
        return None


def _load_signal_engine(pin: int):
    try:
        from services.signal_engine import SignalEngine
        return SignalEngine(pin=pin)
    except Exception as exc:
        logger.warning("SignalEngine not available: %s", exc)
        return None


def _load_news_scanner(pin: int, poll_interval: int = 120):
    try:
        from services.news_scanner import NewsScanner
        return NewsScanner(pin=pin, poll_interval=poll_interval)
    except Exception as exc:
        logger.warning("NewsScanner not available: %s", exc)
        return None


def _load_oanda(pin: int, mode: str):
    try:
        from brokers.oanda_connector import OandaConnector
        env = "practice" if mode == "paper" else "live"
        return OandaConnector(pin=pin, environment=env)
    except Exception as exc:
        logger.warning("OandaConnector not available: %s", exc)
        return None


def _load_coinbase(pin: int, mode: str):
    try:
        from brokers.coinbase_connector import CoinbaseConnector
        sandbox = mode == "paper"
        return CoinbaseConnector(pin=pin, sandbox=sandbox)
    except Exception as exc:
        logger.warning("CoinbaseConnector not available: %s", exc)
        return None


# ------------------------------------------------------------------
# Main runner
# ------------------------------------------------------------------

class HeadlessRunner:
    """
    Orchestrates the full headless multi-broker trading loop.

    The runner does NOT place real trades on its own — it delegates
    execution decisions to the broker connectors based on the combined
    output of the signal engine and news scanner.  All risk rules are
    enforced by the loaded RickCharter instance.

    Loop cadence:
      Every SIGNAL_INTERVAL seconds:
        1. Evaluate cross-market signals
        2. Read current news confidence snapshot
        3. If confidence >= MIN_CONFIDENCE and regime != RISK_OFF:
             → pass signal to OANDA and Coinbase connectors for consideration
        4. Sleep until next cycle
    """

    SIGNAL_INTERVAL = 60     # seconds between signal evaluation cycles
    MIN_CONFIDENCE  = 45.0   # minimum confidence score to allow trade consideration

    def __init__(self, pin: int = 841921, mode: str = "paper"):
        self._pin  = pin
        self._mode = mode.lower()
        self._running = False

        logger.info("=" * 60)
        logger.info("HeadlessRunner initialising — mode=%s", self._mode)
        logger.info("=" * 60)

        self._charter      = _load_charter(pin)
        self._signal_engine = _load_signal_engine(pin)
        self._news_scanner  = _load_news_scanner(pin)
        self._oanda         = _load_oanda(pin, self._mode)
        self._coinbase      = _load_coinbase(pin, self._mode)

        self._report_readiness()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the headless runner loop (blocking)."""
        self._running = True

        # Start background news scanner
        if self._news_scanner:
            self._news_scanner.start()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT,  self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        logger.info("HeadlessRunner started. Press Ctrl+C to stop.")
        self._loop()

    def stop(self) -> None:
        """Gracefully stop all background services."""
        self._running = False
        if self._news_scanner:
            self._news_scanner.stop()
        logger.info("HeadlessRunner stopped.")

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        while self._running:
            try:
                self._tick()
            except Exception as exc:
                logger.error("Tick error: %s", exc, exc_info=True)
            time.sleep(self.SIGNAL_INTERVAL)

    def _tick(self) -> None:
        """Single evaluation cycle."""
        now = datetime.now(timezone.utc).isoformat()

        # 1. Evaluate cross-market signals
        signal = None
        if self._signal_engine:
            try:
                signal = self._signal_engine.evaluate()
                logger.info(
                    "[%s] Signal | BTC: %.3f | Gold: %.3f | DXY: %.3f | "
                    "Corr: %.3f | Regime: %s | Confidence: %.1f | MacroRisk: %s",
                    now,
                    signal.btc_momentum,
                    signal.gold_momentum,
                    signal.dxy_trend,
                    signal.btc_gold_correlation,
                    signal.regime,
                    signal.confidence_score,
                    signal.macro_risk_flag,
                )
            except Exception as exc:
                logger.warning("SignalEngine evaluate failed: %s", exc)

        # 2. News confidence snapshot
        news_snap = None
        if self._news_scanner:
            try:
                news_snap = self._news_scanner.snapshot()
                logger.info(
                    "[%s] News  | Confidence: %.1f | CryptoSentiment: %.3f | "
                    "MacroRisk: %.1f | Items: %d",
                    now,
                    news_snap.overall_confidence,
                    news_snap.crypto_sentiment,
                    news_snap.macro_risk_level,
                    news_snap.active_items,
                )
            except Exception as exc:
                logger.warning("NewsScanner snapshot failed: %s", exc)

        # 3. Gate check — only proceed if conditions are favourable
        if signal is None:
            logger.debug("No signal available; skipping execution gate.")
            return

        if signal.regime == "RISK_OFF":
            logger.info("Regime=RISK_OFF — skipping trade consideration.")
            return

        if signal.confidence_score < self.MIN_CONFIDENCE:
            logger.info(
                "Confidence %.1f < threshold %.1f — skipping.",
                signal.confidence_score, self.MIN_CONFIDENCE
            )
            return

        # 4. Pass signal context to broker adapters
        #    Actual order decisions are made inside each connector's
        #    strategy layer — the runner only provides context.
        self._notify_brokers(signal, news_snap)

    def _notify_brokers(self, signal, news_snap) -> None:
        """
        Forward signal and news context to connected broker adapters.
        Each connector decides independently whether to act.
        """
        context = {
            "signal": signal,
            "news_snapshot": news_snap,
            "mode": self._mode,
        }

        # OANDA — FX / metals / indices
        if self._oanda and hasattr(self._oanda, "on_signal"):
            try:
                self._oanda.on_signal(context)
            except Exception as exc:
                logger.warning("OANDA signal dispatch failed: %s", exc)

        # Coinbase — crypto
        if self._coinbase and hasattr(self._coinbase, "on_signal"):
            try:
                self._coinbase.on_signal(context)
            except Exception as exc:
                logger.warning("Coinbase signal dispatch failed: %s", exc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _report_readiness(self) -> None:
        components = {
            "Charter":      self._charter       is not None,
            "SignalEngine": self._signal_engine  is not None,
            "NewsScanner":  self._news_scanner   is not None,
            "OANDA":        self._oanda          is not None,
            "Coinbase":     self._coinbase        is not None,
        }
        for name, ready in components.items():
            status = "✓" if ready else "✗ (unavailable)"
            logger.info("  %-18s %s", name, status)

    def _handle_shutdown(self, signum, frame) -> None:
        logger.info("Shutdown signal received (%s). Stopping...", signum)
        self.stop()
        sys.exit(0)


# ------------------------------------------------------------------
# CLI entrypoint
# ------------------------------------------------------------------

def main() -> None:
    pin  = int(os.getenv("RICK_PIN", "841921"))
    mode = os.getenv("MODE", "paper").lower()

    if mode not in ("paper", "live"):
        logger.error("Invalid MODE '%s'. Use 'paper' or 'live'.", mode)
        sys.exit(1)

    if mode == "live":
        logger.warning("LIVE mode requested — real money at risk.")

    runner = HeadlessRunner(pin=pin, mode=mode)
    runner.start()


if __name__ == "__main__":
    main()
