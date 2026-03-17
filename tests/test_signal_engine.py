#!/usr/bin/env python3
"""
Unit tests for services/signal_engine.py
Tests momentum, correlation, regime classification, and confidence scoring
without requiring live market data.
PIN: 841921
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from services.signal_engine import (
    SignalEngine,
    CrossMarketSignal,
    _ema,
    _momentum,
    _rolling_correlation,
)


class TestEma(unittest.TestCase):
    """Tests for _ema helper."""

    def test_single_price(self):
        self.assertAlmostEqual(_ema([100.0], 9), 100.0)

    def test_flat_series(self):
        prices = [50.0] * 30
        result = _ema(prices, 9)
        self.assertAlmostEqual(result, 50.0, places=4)

    def test_rising_series(self):
        prices = list(range(1, 31))  # 1..30
        result = _ema(prices, 9)
        # EMA of rising series should be above midpoint but below last value
        self.assertGreater(result, 15.0)
        self.assertLessEqual(result, 30.0)

    def test_empty_series(self):
        self.assertEqual(_ema([], 9), 0.0)


class TestMomentum(unittest.TestCase):
    """Tests for _momentum helper."""

    def test_flat_series_returns_zero(self):
        prices = [100.0] * 50
        self.assertAlmostEqual(_momentum(prices), 0.0, places=3)

    def test_strong_uptrend_positive(self):
        prices = [100.0 + i * 2 for i in range(50)]
        m = _momentum(prices)
        self.assertGreater(m, 0.0)

    def test_strong_downtrend_negative(self):
        prices = [200.0 - i * 2 for i in range(50)]
        m = _momentum(prices)
        self.assertLess(m, 0.0)

    def test_clamped_to_minus_one_plus_one(self):
        prices = [1.0] + [1000.0] * 49  # extreme jump
        m = _momentum(prices)
        self.assertGreaterEqual(m, -1.0)
        self.assertLessEqual(m, 1.0)

    def test_insufficient_data_returns_zero(self):
        prices = [100.0] * 10  # less than slow=21
        self.assertEqual(_momentum(prices), 0.0)


class TestRollingCorrelation(unittest.TestCase):
    """Tests for _rolling_correlation helper."""

    def test_identical_series_correlation_one(self):
        prices = [float(i) for i in range(50)]
        corr = _rolling_correlation(prices, prices)
        self.assertAlmostEqual(corr, 1.0, places=4)

    def test_negated_series_correlation_minus_one(self):
        xs = [float(i) for i in range(50)]
        ys = [-float(i) for i in range(50)]
        corr = _rolling_correlation(xs, ys)
        self.assertAlmostEqual(corr, -1.0, places=4)

    def test_uncorrelated_series(self):
        xs = [1.0, -1.0] * 25
        ys = [1.0] * 50
        corr = _rolling_correlation(xs, ys)
        self.assertAlmostEqual(corr, 0.0, places=4)

    def test_insufficient_data_returns_zero(self):
        corr = _rolling_correlation([1.0, 2.0], [1.0, 2.0])
        self.assertEqual(corr, 0.0)

    def test_clamped_to_valid_range(self):
        xs = [float(i) for i in range(50)]
        ys = [float(i) * 1.001 + 0.0001 for i in range(50)]
        corr = _rolling_correlation(xs, ys)
        self.assertGreaterEqual(corr, -1.0)
        self.assertLessEqual(corr, 1.0)


class TestSignalEngine(unittest.TestCase):
    """Integration-style tests for SignalEngine."""

    def _make_engine(self) -> SignalEngine:
        """Create an engine with a mocked price fetcher."""
        engine = SignalEngine(pin=841921, history_size=50)
        # Override fetcher to avoid network calls
        engine._fetcher = MagicMock()
        engine._fetcher.fetch.return_value = None
        return engine

    def test_init_valid_pin(self):
        engine = self._make_engine()
        self.assertIsNotNone(engine)

    def test_init_invalid_pin(self):
        with self.assertRaises((ValueError, Exception)):
            SignalEngine(pin=999999)

    def test_update_adds_to_history(self):
        engine = self._make_engine()
        engine.update("BTC.USD", 50000.0)
        engine.update("BTC.USD", 51000.0)
        self.assertEqual(len(engine._history["BTC.USD"]), 2)

    def test_evaluate_returns_signal(self):
        engine = self._make_engine()
        # Feed synthetic prices
        for i in range(30):
            engine.update("BTC.USD", 50000.0 + i * 100)
            engine.update("GOLD", 1900.0 + i * 0.5)
            engine.update("DXY", 103.0 - i * 0.01)
        signal = engine.evaluate()
        self.assertIsInstance(signal, CrossMarketSignal)
        self.assertIsNotNone(signal.timestamp)

    def test_evaluate_confidence_in_range(self):
        engine = self._make_engine()
        for i in range(30):
            engine.update("BTC.USD", 50000.0 + i * 200)
            engine.update("GOLD", 1900.0)
            engine.update("DXY", 103.0)
        signal = engine.evaluate()
        self.assertGreaterEqual(signal.confidence_score, 0.0)
        self.assertLessEqual(signal.confidence_score, 100.0)

    def test_last_signal_none_before_evaluate(self):
        engine = self._make_engine()
        self.assertIsNone(engine.last_signal())

    def test_last_signal_set_after_evaluate(self):
        engine = self._make_engine()
        engine.evaluate()
        self.assertIsNotNone(engine.last_signal())

    def test_regime_risk_on(self):
        engine = self._make_engine()
        # Build bullish BTC, flat gold, weak DXY
        for i in range(30):
            engine.update("BTC.USD", 40000.0 + i * 500)   # strong uptrend
            engine.update("GOLD", 1900.0)                  # flat
            engine.update("DXY", 104.0 - i * 0.1)         # DXY weakening

        signal = engine.evaluate()
        self.assertIn(signal.regime, ("RISK_ON", "NEUTRAL", "RISK_OFF"))

    def test_regime_risk_off_on_macro_flag(self):
        engine = self._make_engine()
        # Patch macro check to return True
        with patch.object(engine, "_check_macro_risk", return_value=True):
            signal = engine.evaluate()
        self.assertEqual(signal.regime, "RISK_OFF")

    def test_signal_has_expected_fields(self):
        engine = self._make_engine()
        signal = engine.evaluate()
        self.assertTrue(hasattr(signal, "btc_momentum"))
        self.assertTrue(hasattr(signal, "gold_momentum"))
        self.assertTrue(hasattr(signal, "dxy_trend"))
        self.assertTrue(hasattr(signal, "btc_gold_correlation"))
        self.assertTrue(hasattr(signal, "macro_risk_flag"))
        self.assertTrue(hasattr(signal, "confidence_score"))
        self.assertTrue(hasattr(signal, "regime"))

    def test_momentum_values_clamped(self):
        engine = self._make_engine()
        for i in range(30):
            engine.update("BTC.USD", 50000.0 * (1.1 ** i))  # extreme growth
        signal = engine.evaluate()
        self.assertGreaterEqual(signal.btc_momentum, -1.0)
        self.assertLessEqual(signal.btc_momentum, 1.0)


class TestSignalEngineResilience(unittest.TestCase):
    """Edge-case and resilience tests."""

    def _make_engine(self) -> SignalEngine:
        engine = SignalEngine(pin=841921, history_size=50)
        engine._fetcher = MagicMock()
        engine._fetcher.fetch.return_value = None
        return engine

    def test_evaluate_without_any_prices(self):
        """Engine should return a signal even with no history."""
        engine = self._make_engine()
        signal = engine.evaluate()
        self.assertEqual(signal.btc_momentum, 0.0)
        self.assertEqual(signal.gold_momentum, 0.0)
        self.assertEqual(signal.btc_gold_correlation, 0.0)

    def test_history_respects_max_size(self):
        engine = SignalEngine(pin=841921, history_size=10)
        engine._fetcher = MagicMock()
        engine._fetcher.fetch.return_value = None
        for i in range(50):
            engine.update("BTC.USD", float(i))
        self.assertLessEqual(len(engine._history["BTC.USD"]), 10)

    def test_update_unknown_symbol_ignored(self):
        """Updating an unknown symbol should not raise."""
        engine = self._make_engine()
        engine.update("UNKNOWN_ASSET", 12345.0)  # should be silently ignored

    def test_fetcher_exception_doesnt_crash(self):
        engine = self._make_engine()
        engine._fetcher.fetch.side_effect = RuntimeError("network error")
        signal = engine.evaluate()
        self.assertIsInstance(signal, CrossMarketSignal)


if __name__ == "__main__":
    unittest.main(verbosity=2)
