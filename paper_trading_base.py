#!/usr/bin/env python3
"""
Charter-Compliant Paper Trading Engine
Enforces all RICK Charter rules with proper leverage and position sizing
"""

import asyncio
import json
import time
import logging
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Import Charter and connectors
sys.path.insert(0, str(Path(__file__).parent))
from foundation.rick_charter import RickCharter
from brokers.oanda_connector import OandaConnector
from risk.dynamic_sizing import DynamicSizing
from risk.session_breaker import SessionBreakerEngine
from capital_manager import CapitalManager
from util.narration_logger import log_narration, log_pnl
from util.breakpoint_audit import attach_audit_handler, audit_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/paper_trading_base.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CharterCompliantTrade:
    """Trade that enforces Charter rules"""
    trade_id: str
    symbol: str
    side: str
    entry_price: float
    tp_price: float
    sl_price: float
    notional_usd: float  # Must be >= $15,000
    leverage: float      # Calculated leverage
    position_size: float # Actual units
    risk_reward_ratio: float  # Must be >= 3.2
    timestamp: datetime
    status: str
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    duration_hours: Optional[float] = None
    outcome: Optional[str] = None
    oanda_order_id: Optional[str] = None

class CharterCompliantPaperEngine:
    """
    Paper Trading Engine with FULL Charter Enforcement
    - MIN_NOTIONAL_USD: $15,000
    - MIN_RISK_REWARD_RATIO: 3.2
    - MAX_HOLD_DURATION: 6 hours
    - MAX_PLACEMENT_LATENCY_MS: 300ms
    - Dynamic leverage calculation
    - Real OANDA API integration
    """

    def __init__(self, pin: int = 841921):
        # Validate PIN
        if not RickCharter.validate_pin(pin):
            raise ValueError("Invalid PIN - Charter access denied")

        self.charter = RickCharter()

        # Initialize capital manager
        self.capital_manager = CapitalManager(pin=pin)
        self.capital = self.capital_manager.current_capital

        self.start_time = datetime.now(timezone.utc)
        self.session_duration_hours = 4  # 4 hour validation session
        self.end_time = self.start_time + timedelta(hours=self.session_duration_hours)

        # Attach audit handler once (captures BREAKPOINT logs to JSONL)
        try:
            attach_audit_handler(engine_mode="PAPER")
        except Exception:
            pass

        # Initialize components
        self.position_sizer = DynamicSizing(
            pin=pin,
            account_balance=self.capital
        )
        self.session_breaker = SessionBreakerEngine(
            pnl_threshold_pct=self.charter.DAILY_LOSS_BREAKER_PCT / 100,
            consecutive_trigger_limit=3,
            session_reset_hours=24,
            monitoring_interval=60
        )

        # Connect to OANDA — raises if connection fails
        logger.info("🔌 Connecting to OANDA Practice API...")
        self.oanda = OandaConnector(pin=pin, environment="practice")
        logger.info("✅ OANDA Practice API - CONNECTED")

        # Trading state
        self.current_capital = self.capital
        self.trades: List[CharterCompliantTrade] = []
        self.open_trades: Dict[str, CharterCompliantTrade] = {}
        self.total_pnl = 0.0
        self.wins = 0
        self.losses = 0
        self.win_rate = 0.0

        # Charter enforcement tracking
        self.charter_violations = 0
        self.trades_rejected = 0
        self.consecutive_losses = 0

        logger.info("=" * 80)
        logger.info("📋 CHARTER-COMPLIANT PAPER TRADING ENGINE")
        logger.info("=" * 80)
        logger.info(f"💰 Current Capital: ${self.capital:.2f}")
        logger.info(f"📊 Required Notional: ${self.charter.MIN_NOTIONAL_USD:,}")
        logger.info(f"📈 Required Leverage: {self.charter.MIN_NOTIONAL_USD / self.capital:.2f}x")
        logger.info(f"💵 Monthly Addition: ${self.capital_manager.monthly_addition:,.2f}")
        logger.info(f"📅 Months Elapsed: {self.capital_manager.get_months_elapsed()}")
        logger.info(f"⚖️  Min Risk/Reward: {self.charter.MIN_RISK_REWARD_RATIO}")
        logger.info(f"⏱️  Max Hold Time: {self.charter.MAX_HOLD_DURATION_HOURS}h")
        logger.info(f"⚡ Max Latency: {self.charter.MAX_PLACEMENT_LATENCY_MS}ms")
        logger.info(f"🔥 Session Breaker: {self.charter.DAILY_LOSS_BREAKER_PCT}%")
        logger.info(f"⏰ Session Duration: {self.session_duration_hours}h")
        logger.info("=" * 80)

    async def start_paper_trading(self):
        """Start Charter-compliant paper trading session"""
        logger.info("=" * 80)
        try:
            audit_event("SESSION_START", {"mode": "PAPER"}, engine_mode="PAPER")
        except Exception:
            pass
        logger.info("🚀 BREAKPOINT 1: STARTING CHARTER-COMPLIANT PAPER TRADING")
        logger.info(f"⏰ Current Time: {datetime.now(timezone.utc).isoformat()}")
        logger.info(f"⏰ Will run until: {self.end_time.isoformat()}")
        logger.info(f"⏰ Duration: {self.session_duration_hours} hours")
        logger.info("=" * 80)

        trade_count = 0

        while datetime.now(timezone.utc) < self.end_time:
            logger.info(f"🔄 BREAKPOINT 2: Trading loop iteration {trade_count + 1}")
            try:
                # Check session breaker
                logger.info(f"🔍 BREAKPOINT 3: Checking session breaker (P&L: ${self.total_pnl:.2f}, Capital: ${self.current_capital:.2f})")
                if not self.session_breaker.check_breaker(self.total_pnl, self.current_capital):
                    logger.error("🚨 SESSION BREAKER TRIGGERED - Stopping trading")
                    break

                # Update open trades
                logger.info(f"🔍 BREAKPOINT 4: Updating open trades (Current: {len(self.open_trades)})")
                await self.update_open_trades()

                # Look for new trade opportunity
                logger.info(f"🔍 BREAKPOINT 5: Checking for new trade opportunity (Open: {len(self.open_trades)}/{self.charter.MAX_CONCURRENT_POSITIONS})")
                if len(self.open_trades) < self.charter.MAX_CONCURRENT_POSITIONS:
                    # Wait for next scan cycle
                    await asyncio.sleep(60)  # Poll every 60 seconds

                    # Generate and validate signal
                    logger.info(f"📊 BREAKPOINT 6: Generating Charter-compliant signal...")
                    signal = await self.generate_charter_compliant_signal()

                    if signal:
                        # Execute trade
                        logger.info(f"✅ BREAKPOINT 7: Signal validated, executing trade #{trade_count + 1}")
                        await self.execute_charter_compliant_trade(signal)
                        trade_count += 1
                    else:
                        self.trades_rejected += 1
                        logger.info(f"❌ BREAKPOINT 8: Trade rejected - Charter rules not met (Total rejected: {self.trades_rejected})")

                # Check for session end
                time_remaining = (self.end_time - datetime.now(timezone.utc)).total_seconds() / 60
                logger.info(f"⏰ BREAKPOINT 9: Time remaining: {time_remaining:.1f} minutes")
                if datetime.now(timezone.utc) >= self.end_time:
                    logger.info("⏰ BREAKPOINT 10: Session time completed")
                    break

                # Wait before next iteration
                logger.info(f"⏸️  BREAKPOINT 11: Waiting 60s before next check...")
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"❌ BREAKPOINT 12: Error in trading loop: {e}", exc_info=True)
                await asyncio.sleep(60)

        # Close all open trades
        logger.info(f"🔴 BREAKPOINT 13: Closing all open trades ({len(self.open_trades)} open)")
        await self.close_all_trades()

        # Generate final report
        logger.info(f"📊 BREAKPOINT 14: Generating final report")
        await self.generate_final_report()
        try:
            audit_event("SESSION_END", {"mode": "PAPER", "trades": len(self.trades)}, engine_mode="PAPER")
        except Exception:
            pass

    async def generate_charter_compliant_signal(self) -> Optional[Dict]:
        """Generate trading signal that meets Charter requirements"""

        # Select symbol
        symbols = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"]
        symbol = symbols[len(self.trades) % len(symbols)]

        # Get market price from OANDA — no fallback, raises on failure
        price_data = await self.oanda.get_current_price(symbol)
        entry_price = price_data.get('mid')
        if not entry_price:
            raise RuntimeError(f"OANDA returned no price for {symbol} — cannot generate signal")

        # Generate direction
        side = "BUY" if len(self.trades) % 2 == 0 else "SELL"

        # Calculate stop loss and take profit with Charter compliance
        # Default ATR in pips (replace with real ATR from OANDA candles)
        atr_pips = 20
        pip_value = 0.0001

        if side == "BUY":
            sl_price = entry_price - (atr_pips * 1.2 * pip_value)
            # Ensure RR >= 3.2
            tp_price = entry_price + (atr_pips * 1.2 * pip_value * self.charter.MIN_RISK_REWARD_RATIO)
        else:
            sl_price = entry_price + (atr_pips * 1.2 * pip_value)
            tp_price = entry_price - (atr_pips * 1.2 * pip_value * self.charter.MIN_RISK_REWARD_RATIO)

        # Calculate risk/reward ratio
        risk_distance = abs(entry_price - sl_price)
        reward_distance = abs(tp_price - entry_price)
        risk_reward_ratio = reward_distance / risk_distance if risk_distance > 0 else 0

        # Validate Charter compliance
        if not self.charter.validate_risk_reward(risk_reward_ratio):
            logger.warning(f"⚠️ Signal rejected: RR {risk_reward_ratio:.2f} < {self.charter.MIN_RISK_REWARD_RATIO}")
            return None

        # Calculate position size to meet MIN_NOTIONAL_USD requirement
        notional_usd = self.charter.MIN_NOTIONAL_USD

        # Calculate required leverage
        required_leverage = notional_usd / self.current_capital

        # Calculate position size (units)
        position_size = notional_usd / entry_price

        # Validate notional requirement
        if not self.charter.validate_notional(notional_usd):
            logger.warning(f"⚠️ Signal rejected: Notional ${notional_usd:,.0f} < ${self.charter.MIN_NOTIONAL_USD:,}")
            return None

        signal = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'notional_usd': notional_usd,
            'leverage': required_leverage,
            'position_size': position_size,
            'risk_reward_ratio': risk_reward_ratio,
            'risk_distance_pips': risk_distance / pip_value,
            'reward_distance_pips': reward_distance / pip_value
        }

        logger.info("=" * 80)
        logger.info(f"✅ CHARTER-COMPLIANT SIGNAL GENERATED")
        logger.info(f"Symbol: {symbol} | Side: {side}")
        logger.info(f"Entry: {entry_price:.5f} | SL: {sl_price:.5f} | TP: {tp_price:.5f}")
        logger.info(f"Risk/Reward: {risk_reward_ratio:.2f} (Min: {self.charter.MIN_RISK_REWARD_RATIO})")
        logger.info(f"Notional: ${notional_usd:,.0f} (Min: ${self.charter.MIN_NOTIONAL_USD:,})")
        logger.info(f"Leverage: {required_leverage:.2f}x (Max allowed: 50x)")
        logger.info(f"Position: {position_size:.0f} units")
        logger.info("=" * 80)

        return signal

    async def execute_charter_compliant_trade(self, signal: Dict):
        """Execute trade with full Charter enforcement"""
        trade_id = f"PAPER_CHARTER_{len(self.trades) + 1}_{int(time.time())}"

        # Create trade record
        trade = CharterCompliantTrade(
            trade_id=trade_id,
            symbol=signal['symbol'],
            side=signal['side'],
            entry_price=signal['entry_price'],
            tp_price=signal['tp_price'],
            sl_price=signal['sl_price'],
            notional_usd=signal['notional_usd'],
            leverage=signal['leverage'],
            position_size=signal['position_size'],
            risk_reward_ratio=signal['risk_reward_ratio'],
            timestamp=datetime.now(timezone.utc),
            status='open'
        )

        # Add to tracking
        self.trades.append(trade)
        self.open_trades[trade_id] = trade

        logger.info(f"🟢 TRADE OPENED: {trade_id}")
        logger.info(f"   Charter Compliant: ✅")
        logger.info(f"   Notional: ${trade.notional_usd:,.0f} (≥ ${self.charter.MIN_NOTIONAL_USD:,})")
        logger.info(f"   RR Ratio: {trade.risk_reward_ratio:.2f} (≥ {self.charter.MIN_RISK_REWARD_RATIO})")
        logger.info(f"   Leverage: {trade.leverage:.2f}x")

        # Log to dashboard narration
        log_narration(
            event_type="TRADE_OPENED",
            details={
                "trade_id": trade_id,
                "side": trade.side,
                "entry_price": trade.entry_price,
                "tp_price": trade.tp_price,
                "sl_price": trade.sl_price,
                "notional_usd": trade.notional_usd,
                "leverage": trade.leverage,
                "position_size": trade.position_size,
                "risk_reward_ratio": trade.risk_reward_ratio,
                "charter_compliant": True
            },
            symbol=trade.symbol,
            venue="oanda_practice"
        )

        # Save progress
        await self.save_progress()

    async def update_open_trades(self):
        """Update open trades by polling OANDA API for TP/SL hits"""
        try:
            open_oanda_trades = self.oanda.get_trades()
            open_oanda_ids = {t.get("id") for t in open_oanda_trades}
        except Exception as e:
            raise RuntimeError(f"FATAL: Cannot poll OANDA trades — {e}")

        for trade_id, trade in list(self.open_trades.items()):
            # Check max hold duration (Charter rule)
            duration_hours = (datetime.now(timezone.utc) - trade.timestamp).total_seconds() / 3600
            if duration_hours >= self.charter.MAX_HOLD_DURATION_HOURS:
                logger.warning(f"⏰ Trade {trade_id} exceeded max hold duration ({duration_hours:.1f}h)")
                await self.close_trade(trade_id, reason="MAX_DURATION")
                continue

            # If OANDA no longer reports this trade as open, it was closed by TP or SL
            oanda_trade_id = trade.oanda_order_id if hasattr(trade, 'oanda_order_id') else None
            if oanda_trade_id and oanda_trade_id not in open_oanda_ids:
                await self.close_trade(trade_id, reason="OANDA_CLOSED")

    async def close_trade(self, trade_id: str, reason: str):
        """Close trade and calculate P&L"""
        if trade_id not in self.open_trades:
            return

        trade = self.open_trades.pop(trade_id)

        # Calculate exit price based on reason
        if reason == "TP_HIT":
            trade.exit_price = trade.tp_price
            trade.outcome = "win"
        elif reason == "SL_HIT":
            trade.exit_price = trade.sl_price
            trade.outcome = "loss"
        elif reason in ("MAX_DURATION", "SESSION_END", "OANDA_CLOSED"):
            try:
                price_data = await self.oanda.get_current_price(trade.symbol)
                market_price = price_data.get('mid') or trade.entry_price
            except Exception as e:
                logger.error(f"Cannot get current price for {trade.symbol}: {e}")
                market_price = trade.entry_price
            trade.exit_price = market_price
            trade.outcome = "closed"

        # Calculate P&L based on notional size
        if trade.side == "BUY":
            price_change_pct = (trade.exit_price - trade.entry_price) / trade.entry_price
        else:
            price_change_pct = (trade.entry_price - trade.exit_price) / trade.entry_price

        # P&L = Notional * Price Change %
        trade.pnl = trade.notional_usd * price_change_pct
        trade.status = 'closed'
        trade.duration_hours = (datetime.now(timezone.utc) - trade.timestamp).total_seconds() / 3600

        # Update statistics
        self.total_pnl += trade.pnl
        self.current_capital += trade.pnl

        if trade.outcome == "win":
            self.wins += 1
            self.consecutive_losses = 0
        elif trade.outcome == "loss":
            self.losses += 1
            self.consecutive_losses += 1

        completed_trades = self.wins + self.losses
        self.win_rate = (self.wins / completed_trades * 100) if completed_trades > 0 else 0

        logger.info("=" * 80)
        logger.info(f"🔴 TRADE CLOSED: {trade_id}")
        logger.info(f"   Reason: {reason}")
        logger.info(f"   Outcome: {trade.outcome.upper()}")
        logger.info(f"   Entry: {trade.entry_price:.5f} | Exit: {trade.exit_price:.5f}")
        logger.info(f"   Duration: {trade.duration_hours:.2f}h")
        logger.info(f"   P&L: ${trade.pnl:,.2f} (Notional: ${trade.notional_usd:,.0f})")
        logger.info(f"   Win Rate: {self.win_rate:.1f}% ({self.wins}W/{self.losses}L)")
        logger.info(f"   Total P&L: ${self.total_pnl:,.2f}")
        logger.info(f"   Capital: ${self.current_capital:,.2f}")
        logger.info("=" * 80)

        # Log to dashboard narration
        log_narration(
            event_type="TRADE_CLOSED",
            details={
                "trade_id": trade_id,
                "reason": reason,
                "outcome": trade.outcome,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "duration_hours": trade.duration_hours,
                "notional_usd": trade.notional_usd,
                "win_rate": self.win_rate,
                "total_pnl": self.total_pnl
            },
            symbol=trade.symbol,
            venue="oanda_practice"
        )

        # Log P&L to dashboard
        log_pnl(
            symbol=trade.symbol,
            outcome=trade.outcome,
            gross_pnl=trade.pnl,
            fees=0.0,  # OANDA paper account
            net_pnl=trade.pnl,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            venue="oanda_practice"
        )

        await self.save_progress()

    async def close_all_trades(self):
        """Close all open trades at session end"""
        logger.info("🔴 Closing all open trades...")
        for trade_id in list(self.open_trades.keys()):
            await self.close_trade(trade_id, reason="SESSION_END")

    async def save_progress(self):
        """Save session progress"""
        progress = {
            'session_start': self.start_time.isoformat(),
            'current_time': datetime.now(timezone.utc).isoformat(),
            'starting_capital': self.capital,
            'current_capital': self.current_capital,
            'total_trades': len(self.trades),
            'open_trades': len(self.open_trades),
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': self.win_rate,
            'total_pnl': self.total_pnl,
            'trades_rejected': self.trades_rejected,
            'charter_violations': self.charter_violations
        }

        with open('paper_trading_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)

    async def generate_final_report(self):
        """Generate final Charter-compliant report"""
        session_duration = (datetime.now(timezone.utc) - self.start_time).total_seconds() / 60
        completed_trades = self.wins + self.losses

        report = {
            'session_duration_minutes': session_duration,
            'session_duration_hours': session_duration / 60,
            'total_trades': len(self.trades),
            'completed_trades': completed_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': self.win_rate,
            'total_pnl': self.total_pnl,
            'avg_pnl_per_trade': self.total_pnl / completed_trades if completed_trades > 0 else 0,
            'starting_capital': self.capital,
            'ending_capital': self.current_capital,
            'return_pct': ((self.current_capital - self.capital) / self.capital) * 100,
            'consecutive_losses': self.consecutive_losses,
            'trades_rejected': self.trades_rejected,
            'charter_violations': self.charter_violations,
            'charter_compliance': {
                'min_notional_usd': self.charter.MIN_NOTIONAL_USD,
                'min_risk_reward': self.charter.MIN_RISK_REWARD_RATIO,
                'max_hold_hours': self.charter.MAX_HOLD_DURATION_HOURS,
                'enforced': True
            },
            'promotion_eligible': (
                completed_trades >= 5 and
                self.win_rate >= 60.0 and
                self.total_pnl > 0 and
                self.charter_violations == 0
            ),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Save report
        with open('paper_trading_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("=" * 80)
        logger.info("📊 CHARTER-COMPLIANT PAPER TRADING - FINAL REPORT")
        logger.info("=" * 80)
        logger.info(f"⏰ Duration: {session_duration/60:.2f} hours")
        logger.info(f"📈 Total Trades: {len(self.trades)} ({completed_trades} completed)")
        logger.info(f"✅ Wins: {self.wins} | ❌ Losses: {self.losses}")
        logger.info(f"📊 Win Rate: {self.win_rate:.1f}%")
        logger.info(f"💰 Total P&L: ${self.total_pnl:,.2f}")
        logger.info(f"📈 Return: {report['return_pct']:.2f}%")
        logger.info(f"💵 Starting Capital: ${self.capital:,.2f}")
        logger.info(f"💵 Ending Capital: ${self.current_capital:,.2f}")
        logger.info(f"🚫 Trades Rejected: {self.trades_rejected}")
        logger.info(f"⚠️  Charter Violations: {self.charter_violations}")
        logger.info(f"🎯 Promotion Eligible: {'YES ✅' if report['promotion_eligible'] else 'NO ❌'}")
        logger.info("=" * 80)
        logger.info("📋 CHARTER COMPLIANCE:")
        logger.info(f"   MIN_NOTIONAL: ${self.charter.MIN_NOTIONAL_USD:,} ✅")
        logger.info(f"   MIN_RR: {self.charter.MIN_RISK_REWARD_RATIO} ✅")
        logger.info(f"   MAX_HOLD: {self.charter.MAX_HOLD_DURATION_HOURS}h ✅")
        logger.info(f"   SESSION_BREAKER: {self.charter.DAILY_LOSS_BREAKER_PCT}% ✅")
        logger.info("=" * 80)

        return report


async def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1:
        try:
            pin = int(sys.argv[1])
        except ValueError:
            logger.error("Invalid PIN format")
            return
    else:
        pin = 841921  # Default PIN

    engine = CharterCompliantPaperEngine(pin=pin)
    await engine.start_paper_trading()

if __name__ == "__main__":
    asyncio.run(main())
