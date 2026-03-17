#!/usr/bin/env python3
"""
Real-time Paper Session Monitor
Watch paper trading progress with live updates
"""

import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

def clear_screen():
    """Clear terminal screen"""
    subprocess.run(['clear'])

def get_paper_pid():
    """Get paper trading engine PID if running"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'paper_trading_engine.py'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            return int(result.stdout.strip().split()[0])
    except Exception:
        pass
    return None

def tail_log(file_path, lines=15):
    """Get last N lines from log file"""
    try:
        result = subprocess.run(
            ['tail', '-n', str(lines), file_path],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception:
        return ""

def parse_latest_trade(log_content):
    """Extract latest trade info from log"""
    lines = log_content.strip().split('\n')
    for line in reversed(lines):
        if 'Paper Trade Result' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                outcome = parts[0].split(':')[-1].strip()
                pnl = parts[1].split('$')[-1].strip() if '$' in parts[1] else "0"
                capital = parts[2].split('$')[-1].strip() if '$' in parts[2] else "0"
                win_rate = parts[3].split(':')[-1].strip() if ':' in parts[3] else "0%"
                return {
                    'outcome': outcome,
                    'pnl': pnl,
                    'capital': capital,
                    'win_rate': win_rate
                }
    return None

def get_pnl_summary():
    """Get P&L summary from narration logger"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from util.narration_logger import get_session_summary
        return get_session_summary()
    except Exception:
        return {}

def monitor_session():
    """Monitor paper session with live updates"""
    log_file = Path(__file__).parent.parent / 'logs' / 'paper_trading.log'

    print("🚀 Starting Paper Session Monitor...")
    print("Press Ctrl+C to stop monitoring\n")
    time.sleep(2)

    try:
        while True:
            clear_screen()

            # Header
            print("=" * 80)
            print("📄 PAPER TRADING SESSION MONITOR")
            print("=" * 80)
            print(f"Monitoring: {log_file}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()

            # Check if process is running
            pid = get_paper_pid()
            if pid:
                print(f"✅ Status: RUNNING (PID: {pid})")
            else:
                print("⏸️  Status: NOT RUNNING")
            print()

            # Get P&L summary
            summary = get_pnl_summary()
            if summary and summary.get('total_trades', 0) > 0:
                print("📊 SESSION SUMMARY (from pnl.jsonl)")
                print("-" * 80)
                print(f"  Total Trades:     {summary['total_trades']}")
                print(f"  Wins / Losses:    {summary['wins']} / {summary['losses']}")
                print(f"  Win Rate:         {summary['win_rate']:.1f}%")
                print(f"  Gross P&L:        ${summary['gross_pnl']:.2f}")
                print(f"  Total Fees:       ${summary['total_fees']:.2f}")
                print(f"  Net P&L:          ${summary['net_pnl']:.2f}")
                print()

            # Parse latest trade from log
            log_content = tail_log(str(log_file), lines=20)
            latest_trade = parse_latest_trade(log_content)
            if latest_trade:
                print("🔥 LATEST TRADE")
                print("-" * 80)
                print(f"  Outcome:          {latest_trade['outcome']}")
                print(f"  Trade P&L:        ${latest_trade['pnl']}")
                print(f"  Current Capital:  ${latest_trade['capital']}")
                print(f"  Win Rate:         {latest_trade['win_rate']}")
                print()

            # Recent log tail
            print("📝 RECENT ACTIVITY (last 10 lines)")
            print("-" * 80)
            recent_lines = log_content.strip().split('\n')[-10:]
            for line in recent_lines:
                if len(line) > 78:
                    line = line[:75] + "..."
                print(f"  {line}")
            print()

            print("=" * 80)
            print("Press Ctrl+C to exit | Auto-refresh every 5 seconds")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped")
        print(f"\nTo view full log: tail -f {log_file}")

if __name__ == '__main__':
    monitor_session()
