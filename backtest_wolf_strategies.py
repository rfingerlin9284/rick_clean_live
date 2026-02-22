#!/usr/bin/env python3
"""
Wolf Pack Strategy Backtester
==============================
Backtest BullishWolf, BearishWolf, and SidewaysWolf strategies using
realistic simulated OHLCV data to gauge edge and profitability.

Data generation: Geometric Brownian Motion (GBM) with regime switching.
Execution: ATR-based SL/TP with spread/slippage, charter-compliant RR ≥ 3.2.

PIN: 841921
"""

import json
import math
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from strategies.bullish_wolf import BullishWolf
from strategies.bearish_wolf import BearishWolf
from strategies.sideways_wolf import SidewaysWolf
from rick_charter import RickCharter

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STARTING_CAPITAL = 15_000.0      # Charter minimum notional
RISK_PER_TRADE_PCT = 0.01        # 1 % of capital risked per trade
MIN_RISK_REWARD = RickCharter.MIN_RISK_REWARD_RATIO   # 3.2
FX_SL_ATR_MULT = RickCharter.FX_STOP_LOSS_ATR_MULTIPLIER  # 1.2
LOOKBACK = 60                    # Candles fed into strategy each bar
MAX_HOLD_BARS = 24               # 6 hours at M15; must have this many bars available after entry
_SCAN_BUFFER = MAX_HOLD_BARS + 1 # Bars reserved at end of dataset for exit simulation
SPREAD_PIPS = 0.00015            # Realistic EUR/USD spread
SLIPPAGE_PIPS = 0.00005          # One-way slippage

# Market regimes and their GBM parameters (drift per bar, vol per bar)
# Bars are assumed to be M15 (15-minute candles)
REGIME_PARAMS: Dict[str, Dict] = {
    "BULL_TRENDING": {
        "drift": 2.5e-5,   # positive drift
        "vol":   5e-4,
        "weight": 0.30,
    },
    "BEAR_TRENDING": {
        "drift": -2.5e-5,  # negative drift
        "vol":   5e-4,
        "weight": 0.20,
    },
    "SIDEWAYS": {
        "drift": 0.0,
        "vol":   2.5e-4,
        "weight": 0.30,
    },
    "VOLATILE": {
        "drift": 0.0,
        "vol":   1.0e-3,
        "weight": 0.15,
    },
    "CRISIS": {
        "drift": -5e-5,
        "vol":   2.5e-3,
        "weight": 0.05,
    },
}

# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------

@dataclass
class OHLCVBar:
    """Single OHLCV bar."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    regime: str


def _sample_regime(rng: np.random.Generator) -> str:
    """Sample a market regime according to REGIME_PARAMS weights."""
    names = list(REGIME_PARAMS.keys())
    weights = [REGIME_PARAMS[n]["weight"] for n in names]
    idx = rng.choice(len(names), p=weights)
    return names[idx]


def generate_ohlcv(
    n_bars: int = 5000,
    initial_price: float = 1.1000,
    regime_switch_every: int = 200,
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """
    Generate realistic M15 OHLCV data using GBM with periodic regime switching.

    Args:
        n_bars: Number of M15 candles to generate.
        initial_price: Starting price.
        regime_switch_every: Bars between regime switches (draws a new regime).
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with columns: open, high, low, close, volume, regime
        and a DatetimeIndex.
    """
    rng = np.random.default_rng(seed)
    bars: List[OHLCVBar] = []

    price = initial_price
    regime = _sample_regime(rng)
    base_time = datetime(2020, 1, 1, tzinfo=timezone.utc)

    for i in range(n_bars):
        if i % regime_switch_every == 0:
            regime = _sample_regime(rng)

        params = REGIME_PARAMS[regime]
        drift = params["drift"]
        vol = params["vol"]

        # GBM step for close price
        z = rng.standard_normal()
        ret = drift + vol * z
        close = price * math.exp(ret)

        # Intra-bar range (realistic OHLC from close)
        bar_range = abs(rng.normal(vol * price, vol * price * 0.3))
        bar_range = max(bar_range, vol * price * 0.1)

        open_price = price
        high = max(open_price, close) + bar_range * rng.uniform(0.1, 0.5)
        low = min(open_price, close) - bar_range * rng.uniform(0.1, 0.5)

        # Volume: higher in volatile/crisis regimes
        vol_multiplier = {"VOLATILE": 1.8, "CRISIS": 2.5}.get(regime, 1.0)
        volume = max(rng.normal(10_000 * vol_multiplier, 2_000 * vol_multiplier), 100)

        bars.append(OHLCVBar(
            timestamp=base_time + timedelta(minutes=15 * i),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume,
            regime=regime,
        ))
        price = close

    index = [b.timestamp for b in bars]
    df = pd.DataFrame(
        {
            "open":   [b.open   for b in bars],
            "high":   [b.high   for b in bars],
            "low":    [b.low    for b in bars],
            "close":  [b.close  for b in bars],
            "volume": [b.volume for b in bars],
            "regime": [b.regime for b in bars],
        },
        index=index,
    )
    return df


# ---------------------------------------------------------------------------
# Trade record
# ---------------------------------------------------------------------------

@dataclass
class BacktestTrade:
    """Single simulated trade."""
    trade_id: int
    strategy: str
    entry_bar: int
    entry_price: float
    stop_loss: float
    take_profit: float
    exit_price: float
    direction: str      # BUY or SELL
    risk_usd: float
    pnl_usd: float
    outcome: str        # win / loss / timeout
    bars_held: int
    regime: str
    confidence: float


# ---------------------------------------------------------------------------
# Backtester
# ---------------------------------------------------------------------------

class WolfPackBacktester:
    """
    Walks forward through OHLCV data, generates signals from each Wolf Pack
    strategy, and simulates trade execution.
    """

    def __init__(self, capital: float = STARTING_CAPITAL):
        self.initial_capital = capital
        self.strategies = {
            "BullishWolf":  BullishWolf(pin=RickCharter.PIN),
            "BearishWolf":  BearishWolf(pin=RickCharter.PIN),
            "SidewaysWolf": SidewaysWolf(pin=RickCharter.PIN),
        }

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATR for position sizing and stop placement."""
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - prev_close).abs(),
                (df["low"]  - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return tr.rolling(period).mean()

    def _build_signal_data(self, df: pd.DataFrame, end_idx: int) -> Dict[str, pd.Series]:
        """Extract LOOKBACK-bar window ending at end_idx for strategy input."""
        start = max(0, end_idx - LOOKBACK + 1)
        window = df.iloc[start : end_idx + 1]
        return {
            "close":  window["close"],
            "high":   window["high"],
            "low":    window["low"],
            "volume": window["volume"],
        }

    def _simulate_exit(
        self,
        df: pd.DataFrame,
        entry_bar: int,
        direction: str,
        stop_loss: float,
        take_profit: float,
        max_bars: int = MAX_HOLD_BARS,  # 6-hour max hold at M15
    ) -> Tuple[float, str, int]:
        """
        Walk forward from entry_bar to find the first bar that hits SL or TP.

        Returns:
            (exit_price, outcome, bars_held)
        """
        for offset in range(1, max_bars + 1):
            bar_idx = entry_bar + offset
            if bar_idx >= len(df):
                break

            bar = df.iloc[bar_idx]
            if direction == "BUY":
                if bar["low"] <= stop_loss:
                    return stop_loss, "loss", offset
                if bar["high"] >= take_profit:
                    return take_profit, "win", offset
            else:  # SELL
                if bar["high"] >= stop_loss:
                    return stop_loss, "loss", offset
                if bar["low"] <= take_profit:
                    return take_profit, "win", offset

        # Timeout: exit at last bar close
        last_bar = df.iloc[min(entry_bar + max_bars, len(df) - 1)]
        return last_bar["close"], "timeout", max_bars

    def run(
        self, df: pd.DataFrame, strategy_name: str
    ) -> Tuple[List[BacktestTrade], List[float]]:
        """
        Run a single strategy over the full dataset.

        Returns:
            (trades, equity_curve)
        """
        strategy = self.strategies[strategy_name]
        trades: List[BacktestTrade] = []
        equity = self.initial_capital
        equity_curve = [equity]
        atr_series = self._calculate_atr(df)

        trade_id = 0
        next_entry_bar = 0  # first bar at which we may open a new trade

        for i in range(LOOKBACK, len(df) - _SCAN_BUFFER):
            if i < next_entry_bar:
                continue

            signal_data = self._build_signal_data(df, i)

            try:
                signal = strategy.generate_trade_signal(signal_data)
            except Exception:
                continue

            if not signal.get("trade", False):
                continue

            direction = signal.get("direction", "HOLD")
            if direction not in ("BUY", "SELL"):
                continue

            confidence = signal.get("confidence", 0.0)
            current_price = df["close"].iloc[i]
            atr = atr_series.iloc[i]
            if pd.isna(atr) or atr <= 0:
                continue

            # Entry price accounts for spread/slippage
            if direction == "BUY":
                entry_price = current_price + SPREAD_PIPS + SLIPPAGE_PIPS
                stop_loss   = entry_price - FX_SL_ATR_MULT * atr
                take_profit = entry_price + MIN_RISK_REWARD * FX_SL_ATR_MULT * atr
            else:
                entry_price = current_price - SPREAD_PIPS - SLIPPAGE_PIPS
                stop_loss   = entry_price + FX_SL_ATR_MULT * atr
                take_profit = entry_price - MIN_RISK_REWARD * FX_SL_ATR_MULT * atr

            # Risk in USD: 1 % of equity
            risk_pips = abs(entry_price - stop_loss)
            risk_usd  = equity * RISK_PER_TRADE_PCT

            exit_price, outcome, bars_held = self._simulate_exit(
                df, i, direction, stop_loss, take_profit,
                max_bars=MAX_HOLD_BARS,
            )

            # PnL in USD
            if direction == "BUY":
                pips_moved = exit_price - entry_price
            else:
                pips_moved = entry_price - exit_price

            pnl_usd = (pips_moved / risk_pips) * risk_usd if risk_pips > 0 else 0.0
            equity = max(equity + pnl_usd, 0.01)
            equity_curve.append(equity)

            trade_id += 1
            trades.append(BacktestTrade(
                trade_id=trade_id,
                strategy=strategy_name,
                entry_bar=i,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                exit_price=exit_price,
                direction=direction,
                risk_usd=risk_usd,
                pnl_usd=pnl_usd,
                outcome=outcome,
                bars_held=bars_held,
                regime=df["regime"].iloc[i],
                confidence=confidence,
            ))

            # Advance past the exit bar before looking for a new entry
            next_entry_bar = i + bars_held + 1

        return trades, equity_curve


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def calculate_metrics(trades: List[BacktestTrade], equity_curve: List[float]) -> Dict:
    """
    Calculate edge metrics for a list of trades.

    Returns dict with: win_rate, profit_factor, expectancy_usd,
    sharpe_ratio, max_drawdown_pct, total_trades, total_pnl_usd,
    final_equity, roi_pct, breakdown_by_regime.
    """
    if not trades:
        return {"error": "No trades generated"}

    wins   = [t for t in trades if t.outcome == "win"]
    losses = [t for t in trades if t.outcome == "loss"]

    total_trades = len(trades)
    win_rate = len(wins) / total_trades

    gross_profit = sum(t.pnl_usd for t in wins)
    gross_loss   = abs(sum(t.pnl_usd for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    total_pnl = sum(t.pnl_usd for t in trades)
    expectancy  = total_pnl / total_trades

    # Sharpe ratio (annualised) from equity curve returns
    if len(equity_curve) > 1:
        eq_arr  = np.array(equity_curve)
        rets    = np.diff(eq_arr) / eq_arr[:-1]
        mean_r  = np.mean(rets)
        std_r   = np.std(rets, ddof=1) if np.std(rets) > 0 else 1e-9
        bars_per_year = 252 * 26  # M15 bars per trading year
        sharpe = (mean_r / std_r) * math.sqrt(bars_per_year)
    else:
        sharpe = 0.0

    # Max drawdown %
    eq_arr = np.array(equity_curve)
    peaks  = np.maximum.accumulate(eq_arr)
    dd_pct = np.max((peaks - eq_arr) / peaks) * 100 if len(peaks) else 0.0

    final_equity = equity_curve[-1]
    roi_pct = (final_equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100

    # Breakdown by regime
    regime_stats: Dict[str, Dict] = {}
    for trade in trades:
        r = trade.regime
        if r not in regime_stats:
            regime_stats[r] = {"trades": 0, "wins": 0, "pnl": 0.0}
        regime_stats[r]["trades"] += 1
        if trade.outcome == "win":
            regime_stats[r]["wins"] += 1
        regime_stats[r]["pnl"] += trade.pnl_usd
    for r, s in regime_stats.items():
        s["win_rate"] = round(s["wins"] / s["trades"], 3) if s["trades"] else 0

    return {
        "total_trades":    total_trades,
        "win_rate":        round(win_rate, 4),
        "profit_factor":   round(profit_factor, 3),
        "expectancy_usd":  round(expectancy, 2),
        "sharpe_ratio":    round(sharpe, 3),
        "max_drawdown_pct": round(dd_pct, 2),
        "total_pnl_usd":   round(total_pnl, 2),
        "final_equity":    round(final_equity, 2),
        "roi_pct":         round(roi_pct, 2),
        "breakdown_by_regime": regime_stats,
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_report(results: Dict[str, Dict]) -> None:
    """Print a formatted edge report for all strategies."""
    print()
    print("=" * 70)
    print("  WOLF PACK STRATEGY BACKTEST REPORT")
    print(f"  Simulated on realistic GBM + regime-switching OHLCV data")
    print(f"  Starting Capital : ${STARTING_CAPITAL:,.0f} | Risk/Trade: {RISK_PER_TRADE_PCT*100:.1f}%")
    print(f"  Min RR           : {MIN_RISK_REWARD} | SL: {FX_SL_ATR_MULT}x ATR")
    print("=" * 70)
    for strat, m in results.items():
        if "error" in m:
            print(f"\n  {strat}: {m['error']}")
            continue
        print(f"\n  Strategy : {strat}")
        print(f"  {'Trades':<22}: {m['total_trades']}")
        print(f"  {'Win Rate':<22}: {m['win_rate']*100:.1f}%")
        print(f"  {'Profit Factor':<22}: {m['profit_factor']:.2f}")
        print(f"  {'Expectancy':<22}: ${m['expectancy_usd']:.2f}/trade")
        print(f"  {'Sharpe Ratio':<22}: {m['sharpe_ratio']:.2f}")
        print(f"  {'Max Drawdown':<22}: {m['max_drawdown_pct']:.1f}%")
        print(f"  {'Total PnL':<22}: ${m['total_pnl_usd']:,.2f}")
        print(f"  {'Final Equity':<22}: ${m['final_equity']:,.2f}")
        print(f"  {'ROI':<22}: {m['roi_pct']:.1f}%")
        print(f"  {'Regime Breakdown':<22}:")
        for regime, s in m["breakdown_by_regime"].items():
            print(
                f"    {regime:<20}: "
                f"{s['trades']:>4} trades, "
                f"WR {s['win_rate']*100:>5.1f}%, "
                f"PnL ${s['pnl']:>8,.2f}"
            )
    print()
    print("=" * 70)
    print()


def run_backtest(
    n_bars: int = 5000,
    seed: int = 42,
    save_report: bool = True,
) -> Dict[str, Dict]:
    """
    Run the full Wolf Pack backtest and return per-strategy metrics.

    Args:
        n_bars: Number of M15 candles to simulate.
        seed: RNG seed for reproducibility.
        save_report: If True, writes results to logs/backtest_report.json.

    Returns:
        Dict mapping strategy name to metrics dict.
    """
    df = generate_ohlcv(n_bars=n_bars, seed=seed)
    backtester = WolfPackBacktester()
    results: Dict[str, Dict] = {}

    for name in ("BullishWolf", "BearishWolf", "SidewaysWolf"):
        trades, equity_curve = backtester.run(df, name)
        results[name] = calculate_metrics(trades, equity_curve)

    if save_report:
        import os
        os.makedirs("logs", exist_ok=True)
        with open("logs/backtest_report.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    results = run_backtest(n_bars=5000, seed=42, save_report=True)
    print_report(results)
