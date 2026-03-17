#!/usr/bin/env python3
"""
Paper Mode Trading Engine
Charter-compliant validation with extended session (2-4 hours)
Uses OANDA practice API with real Charter rules
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Import the Charter-compliant paper engine as base
sys.path.insert(0, str(Path(__file__).parent))
from paper_trading_base import CharterCompliantPaperEngine
from util.breakpoint_audit import attach_audit_handler, audit_event
from util.narration_logger import log_narration

class PaperTradingEngine(CharterCompliantPaperEngine):
    """
    Paper Trading Engine - Extended validation mode
    Inherits all Charter enforcement from paper engine
    Runs longer sessions (2-4 hours) to build pattern library
    """

    def __init__(self, pin: int = 841921):
        # Initialize parent class
        super().__init__(pin=pin)
        try:
            attach_audit_handler(engine_mode="PAPER")
            audit_event("SESSION_INIT", {"mode": "PAPER"}, engine_mode="PAPER")
        except Exception:
            pass

        # Override session duration for PAPER (45 minutes - quick validation)
        self.session_duration_hours = 0.75  # 45 minutes
        self.end_time = self.start_time + __import__('datetime').timedelta(hours=self.session_duration_hours)

        print("=" * 80)
        print("📄 PAPER MODE - Quick Validation Trading (45 minutes)")
        print("=" * 80)
        print("This PAPER session will:")
        print("  ✅ Enforce ALL Charter rules ($15K notional, 3.2 RR, 6h max hold)")
        print("  ✅ Use OANDA Practice API (same as LIVE, but practice account)")
        print("  ✅ Calculate proper leverage (6.6x)")
        print("  ✅ Quick validation session (45 minutes)")
        print("  ✅ Expected 2-3 Charter-compliant trades")
        print(f"  ✅ Session ends at: {self.end_time.isoformat()}")
        print("=" * 80)
        print()

        # Log PAPER initialization
        log_narration(
            event_type="PAPER_INIT",
            details={
                "session_duration_hours": self.session_duration_hours,
                "end_time": self.end_time.isoformat(),
                "charter_rules": "enforced"
            },
            symbol=None,
            venue="OANDA"
        )

    async def generate_final_report(self):
        """Generate PAPER-specific final report"""
        session_duration = (__import__('datetime').datetime.now(__import__('datetime').timezone.utc) - self.start_time).total_seconds() / 60
        completed_trades = self.wins + self.losses

        report = {
            'mode': 'PAPER',
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
                completed_trades >= 3 and  # minimum 3 trades (45 min session)
                self.win_rate >= 60.0 and
                self.total_pnl > 0 and
                self.charter_violations == 0
            ),
            'timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }

        # Save PAPER-specific report
        with open('paper_trading_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        try:
            audit_event("PAPER_FINAL_REPORT", report, engine_mode="PAPER")
        except Exception:
            pass

        # Print summary
        logger = __import__('logging').getLogger(__name__)
        logger.info("=" * 80)
        logger.info("📄 PAPER MODE - FINAL REPORT")
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
        logger.info(f"🎯 Promotion to LIVE Eligible: {'YES ✅' if report['promotion_eligible'] else 'NO ❌'}")
        logger.info("=" * 80)
        logger.info("📋 CHARTER COMPLIANCE:")
        logger.info(f"   MIN_NOTIONAL: ${self.charter.MIN_NOTIONAL_USD:,} ✅")
        logger.info(f"   MIN_RR: {self.charter.MIN_RISK_REWARD_RATIO} ✅")
        logger.info(f"   MAX_HOLD: {self.charter.MAX_HOLD_DURATION_HOURS}h ✅")
        logger.info(f"   SESSION_BREAKER: {self.charter.DAILY_LOSS_BREAKER_PCT}% ✅")
        logger.info("=" * 80)

        if report['promotion_eligible']:
            logger.info("")
            logger.info("🎉 PAPER SESSION SUCCESSFUL")
            logger.info("   Total P&L must be positive")
            if self.charter_violations > 0:
                logger.info(f"   Charter violations: {self.charter_violations}")
            logger.info("")

        # Log final report to narration
        log_narration(
            event_type="PAPER_SESSION_END",
            details={
                "session_duration_hours": report['session_duration_hours'],
                "total_trades": report['total_trades'],
                "completed_trades": report['completed_trades'],
                "wins": report['wins'],
                "losses": report['losses'],
                "win_rate": report['win_rate'],
                "total_pnl": report['total_pnl'],
                "starting_capital": report['starting_capital'],
                "ending_capital": report['ending_capital'],
                "return_pct": report['return_pct'],
                "trades_rejected": report['trades_rejected'],
                "charter_violations": report['charter_violations'],
                "promotion_eligible": report['promotion_eligible']
            },
            symbol=None,
            venue="OANDA"
        )

        return report

    async def generate_charter_compliant_signal(self):
        """Override to add signal generation logging"""
        signal = await super().generate_charter_compliant_signal()

        if signal:
            # Log successful signal generation
            log_narration(
                event_type="SIGNAL_GENERATED",
                details={
                    "symbol": signal['symbol'],
                    "side": signal['side'],
                    "entry_price": signal['entry_price'],
                    "tp_price": signal['tp_price'],
                    "sl_price": signal['sl_price'],
                    "risk_reward_ratio": signal['risk_reward_ratio'],
                    "notional_usd": signal['notional_usd'],
                    "charter_compliant": True
                },
                symbol=signal['symbol'],
                venue="OANDA"
            )
        else:
            # Log signal rejection
            log_narration(
                event_type="SIGNAL_REJECTED",
                details={
                    "reason": "Charter compliance check failed",
                    "min_notional_required": self.charter.MIN_NOTIONAL_USD,
                    "min_rr_required": self.charter.MIN_RISK_REWARD_RATIO
                },
                symbol=None,
                venue="OANDA"
            )

        return signal

    async def close_trade(self, trade_id: str, reason: str):
        """Override to add additional exit logging"""
        # Get trade details before closing
        if trade_id in self.open_trades:
            trade = self.open_trades[trade_id]
            duration_hours = (datetime.now(timezone.utc) - trade.timestamp).total_seconds() / 3600

            # Log TTL enforcement check
            if duration_hours >= self.charter.MAX_HOLD_DURATION_HOURS:
                log_narration(
                    event_type="TTL_ENFORCEMENT",
                    details={
                        "trade_id": trade_id,
                        "duration_hours": round(duration_hours, 2),
                        "max_hold_hours": self.charter.MAX_HOLD_DURATION_HOURS,
                        "reason": "Maximum hold duration reached"
                    },
                    symbol=trade.symbol,
                    venue="oanda_practice"
                )

        # Call parent close_trade (which already logs TRADE_CLOSED)
        await super().close_trade(trade_id, reason)

    async def start_paper_trading(self):
        """Override to add session breaker logging"""
        # Log session start
        log_narration(
            event_type="PAPER_SESSION_START",
            details={
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "session_duration_hours": self.session_duration_hours,
                "starting_capital": self.capital,
                "charter_rules": {
                    "min_notional_usd": self.charter.MIN_NOTIONAL_USD,
                    "min_rr": self.charter.MIN_RISK_REWARD_RATIO,
                    "max_hold_hours": self.charter.MAX_HOLD_DURATION_HOURS,
                    "daily_breaker_pct": self.charter.DAILY_LOSS_BREAKER_PCT
                }
            },
            symbol=None,
            venue="OANDA"
        )

        # Call parent method
        await super().start_paper_trading()


async def main():
    """Main entry point for PAPER trading"""
    import sys

    # Verify mode
    from util.mode_manager import get_mode_info
    mode_info = get_mode_info()

    if mode_info['mode'] != 'PAPER':
        print(f"❌ Error: System is in {mode_info['mode']} mode, not PAPER")
        print("   Switch to PAPER first:")
        print("   $ python3 -c \"from util.mode_manager import switch_mode; switch_mode('PAPER')\"")
        return

    print("✅ System confirmed in PAPER mode")
    print()

    # Get PIN
    if len(sys.argv) > 1:
        try:
            pin = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid PIN format")
            return
    else:
        pin = 841921  # Default PIN

    # Start PAPER trading
    engine = PaperTradingEngine(pin=pin)
    await engine.start_paper_trading()

if __name__ == "__main__":
    asyncio.run(main())
