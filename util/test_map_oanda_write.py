#!/usr/bin/env python3
"""
OANDA Test Narration Writer
Writes test narrations for OANDA orders and AMM trades to narration.jsonl
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
NARRATION_FILE = PROJECT_ROOT / "narration.jsonl"


def write_test_oanda_order(
    symbol: str,
    direction: str,
    units: float,
    price: float,
    order_id: str = None
):
    """Write a test OANDA order to narration.jsonl"""
    if order_id is None:
        order_id = f"test_order_{datetime.now().timestamp()}"
    
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "ORDER_PLACED",
        "symbol": symbol,
        "venue": "oanda",
        "details": {
            "direction": direction.upper(),
            "units": units,
            "price": price,
            "order_id": order_id,
            "status": "FILLED"
        }
    }
    
    with open(NARRATION_FILE, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    print(f"✅ Written OANDA test order: {direction.upper()} {units} {symbol} @ {price}")
    return order_id


def write_test_amm_trade(
    symbol: str,
    entry_price: float,
    exit_price: float,
    units: float,
    pnl: float
):
    """Write a test AMM trade to narration.jsonl"""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "TRADE_CLOSED",
        "symbol": symbol,
        "venue": "amm",
        "details": {
            "entry_price": entry_price,
            "exit_price": exit_price,
            "units": units,
            "pnl": pnl,
            "outcome": "win" if pnl > 0 else "loss"
        }
    }
    
    with open(NARRATION_FILE, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    print(f"✅ Written AMM test trade: {symbol} PnL=${pnl:.2f}")


if __name__ == "__main__":
    print("=" * 60)
    print("OANDA Test Narration Writer")
    print("=" * 60)
    
    # Write sample test data
    order_id = write_test_oanda_order("EUR_USD", "buy", 1000, 1.0850)
    write_test_amm_trade("EUR_USD", 1.0850, 1.0875, 1000, 25.00)
    
    print("\n✅ Test narrations written successfully!")
