#!/usr/bin/env python3
"""
Tests for backtest_wolf_strategies.py
Validates data generation, trade simulation, and metric calculation.
PIN: 841921
"""

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from backtest_wolf_strategies import (
    generate_ohlcv,
    WolfPackBacktester,
    calculate_metrics,
    BacktestTrade,
    run_backtest,
    STARTING_CAPITAL,
    MIN_RISK_REWARD,
    REGIME_PARAMS,
    MAX_HOLD_BARS,
)


class TestGenerateOHLCV(unittest.TestCase):
    """Tests for the OHLCV data generator."""

    def setUp(self):
        self.df = generate_ohlcv(n_bars=300, seed=0)

    def test_correct_length(self):
        self.assertEqual(len(self.df), 300)

    def test_required_columns(self):
        for col in ("open", "high", "low", "close", "volume", "regime"):
            self.assertIn(col, self.df.columns)

    def test_ohlc_relationships(self):
        """High >= max(open, close) and Low <= min(open, close)."""
        self.assertTrue((self.df["high"] >= self.df["open"]).all())
        self.assertTrue((self.df["high"] >= self.df["close"]).all())
        self.assertTrue((self.df["low"] <= self.df["open"]).all())
        self.assertTrue((self.df["low"] <= self.df["close"]).all())

    def test_positive_prices_and_volume(self):
        self.assertTrue((self.df["close"] > 0).all())
        self.assertTrue((self.df["volume"] > 0).all())

    def test_regime_values_are_valid(self):
        valid_regimes = set(REGIME_PARAMS.keys())
        for r in self.df["regime"].unique():
            self.assertIn(r, valid_regimes)

    def test_reproducibility(self):
        df2 = generate_ohlcv(n_bars=300, seed=0)
        pd.testing.assert_frame_equal(self.df, df2)

    def test_different_seeds_differ(self):
        df2 = generate_ohlcv(n_bars=300, seed=99)
        # At least some close prices should differ
        self.assertFalse(self.df["close"].equals(df2["close"]))


class TestWolfPackBacktester(unittest.TestCase):
    """Tests for WolfPackBacktester."""

    @classmethod
    def setUpClass(cls):
        cls.df = generate_ohlcv(n_bars=500, seed=7)
        cls.backtester = WolfPackBacktester()

    def _run(self, name):
        return self.backtester.run(self.df, name)

    def test_bullish_wolf_produces_output(self):
        trades, equity_curve = self._run("BullishWolf")
        self.assertIsInstance(trades, list)
        self.assertIsInstance(equity_curve, list)
        self.assertGreater(len(equity_curve), 0)

    def test_bearish_wolf_produces_output(self):
        trades, equity_curve = self._run("BearishWolf")
        self.assertIsInstance(trades, list)
        self.assertGreater(len(equity_curve), 0)

    def test_sideways_wolf_produces_output(self):
        trades, equity_curve = self._run("SidewaysWolf")
        self.assertIsInstance(trades, list)
        self.assertGreater(len(equity_curve), 0)

    def test_trade_fields_are_populated(self):
        trades, _ = self._run("BullishWolf")
        if trades:
            t = trades[0]
            self.assertIn(t.direction, ("BUY", "SELL"))
            self.assertIn(t.outcome, ("win", "loss", "timeout"))
            self.assertGreater(t.risk_usd, 0)
            self.assertIsInstance(t.pnl_usd, float)

    def test_rr_ratio_respected_on_wins(self):
        """Take-profit distance >= MIN_RISK_REWARD * stop-loss distance for wins."""
        for name in ("BullishWolf", "BearishWolf", "SidewaysWolf"):
            trades, _ = self._run(name)
            for t in trades:
                if t.outcome == "win":
                    sl_dist = abs(t.entry_price - t.stop_loss)
                    tp_dist = abs(t.take_profit - t.entry_price)
                    self.assertGreater(sl_dist, 0, msg=f"{name}: sl_dist is zero")
                    self.assertGreaterEqual(
                        tp_dist / sl_dist,
                        MIN_RISK_REWARD - 1e-6,
                        msg=f"{name}: TP/SL ratio below minimum RR",
                    )

    def test_equity_curve_starts_at_initial_capital(self):
        _, equity_curve = self._run("BullishWolf")
        self.assertAlmostEqual(equity_curve[0], STARTING_CAPITAL, places=2)

    def test_equity_never_negative(self):
        for name in ("BullishWolf", "BearishWolf", "SidewaysWolf"):
            _, equity_curve = self._run(name)
            self.assertTrue(
                all(e > 0 for e in equity_curve),
                msg=f"{name} produced non-positive equity",
            )


class TestCalculateMetrics(unittest.TestCase):
    """Tests for the metrics calculation function."""

    def _make_trades(self, wins: int, losses: int, risk=100.0, rr=3.2):
        trades = []
        for i in range(wins):
            trades.append(BacktestTrade(
                trade_id=i, strategy="Test", entry_bar=i,
                entry_price=1.1, stop_loss=1.09, take_profit=1.132,
                exit_price=1.132, direction="BUY",
                risk_usd=risk, pnl_usd=risk * rr,
                outcome="win", bars_held=10, regime="SIDEWAYS", confidence=0.7,
            ))
        for i in range(losses):
            trades.append(BacktestTrade(
                trade_id=wins + i, strategy="Test", entry_bar=wins + i,
                entry_price=1.1, stop_loss=1.09, take_profit=1.132,
                exit_price=1.09, direction="BUY",
                risk_usd=risk, pnl_usd=-risk,
                outcome="loss", bars_held=5, regime="SIDEWAYS", confidence=0.7,
            ))
        return trades

    def test_empty_trades_returns_error(self):
        result = calculate_metrics([], [STARTING_CAPITAL])
        self.assertIn("error", result)

    def test_win_rate_calculation(self):
        trades = self._make_trades(wins=7, losses=3)
        equity = [STARTING_CAPITAL + i * 10 for i in range(len(trades) + 1)]
        m = calculate_metrics(trades, equity)
        self.assertAlmostEqual(m["win_rate"], 0.7, places=4)

    def test_profit_factor_positive(self):
        trades = self._make_trades(wins=6, losses=4)
        equity = [STARTING_CAPITAL + i * 5 for i in range(len(trades) + 1)]
        m = calculate_metrics(trades, equity)
        self.assertGreater(m["profit_factor"], 0)

    def test_perfect_win_rate(self):
        trades = self._make_trades(wins=10, losses=0)
        equity = [STARTING_CAPITAL + i * 320 for i in range(len(trades) + 1)]
        m = calculate_metrics(trades, equity)
        self.assertAlmostEqual(m["win_rate"], 1.0, places=4)
        self.assertEqual(m["profit_factor"], float("inf"))

    def test_max_drawdown_non_negative(self):
        trades = self._make_trades(wins=5, losses=5)
        equity = [STARTING_CAPITAL - i * 10 for i in range(len(trades) + 1)]
        m = calculate_metrics(trades, equity)
        self.assertGreaterEqual(m["max_drawdown_pct"], 0)

    def test_regime_breakdown_contains_traded_regime(self):
        trades = self._make_trades(wins=3, losses=2)
        equity = [STARTING_CAPITAL] * (len(trades) + 1)
        m = calculate_metrics(trades, equity)
        self.assertIn("SIDEWAYS", m["breakdown_by_regime"])

    def test_roi_positive_on_net_profit(self):
        # 7 wins × $320, 3 losses × -$100 = net +$1940
        trades = self._make_trades(wins=7, losses=3, risk=100.0, rr=3.2)
        equity = [STARTING_CAPITAL + max(0, i * 50) for i in range(len(trades) + 1)]
        m = calculate_metrics(trades, equity)
        self.assertGreater(m["total_pnl_usd"], 0)


class TestRunBacktest(unittest.TestCase):
    """Integration test: run_backtest end-to-end."""

    @classmethod
    def setUpClass(cls):
        cls.results = run_backtest(n_bars=300, seed=1, save_report=False)

    def test_all_strategies_in_results(self):
        for name in ("BullishWolf", "BearishWolf", "SidewaysWolf"):
            self.assertIn(name, self.results)

    def test_results_have_expected_keys(self):
        expected_keys = {
            "total_trades", "win_rate", "profit_factor",
            "expectancy_usd", "sharpe_ratio", "max_drawdown_pct",
            "total_pnl_usd", "final_equity", "roi_pct",
            "breakdown_by_regime",
        }
        for name, m in self.results.items():
            if "error" not in m:
                self.assertTrue(
                    expected_keys.issubset(m.keys()),
                    msg=f"{name} missing keys: {expected_keys - m.keys()}",
                )

    def test_final_equity_is_positive(self):
        for name, m in self.results.items():
            if "error" not in m:
                self.assertGreater(m["final_equity"], 0, msg=f"{name} final equity ≤ 0")

    def test_win_rate_in_valid_range(self):
        for name, m in self.results.items():
            if "error" not in m:
                self.assertGreaterEqual(m["win_rate"], 0.0)
                self.assertLessEqual(m["win_rate"], 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
