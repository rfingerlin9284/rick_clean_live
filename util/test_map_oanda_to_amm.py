#!/usr/bin/env python3
"""
OANDA to AMM Mapper Test
Maps OANDA orders to AMM trades from narration.jsonl
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


def load_narration_events(narration_file: str) -> List[Dict[str, Any]]:
    """Load all events from narration.jsonl"""
    events = []
    try:
        with open(narration_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
        return events
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {narration_file}")
        return []
    except Exception as e:
        print(f"❌ ERROR: Failed to load narration: {e}")
        return []


def map_oanda_to_amm(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map OANDA orders to AMM trades"""
    mappings = []
    
    # Separate OANDA orders and AMM trades
    oanda_orders = [e for e in events if e.get('venue') == 'oanda']
    amm_trades = [e for e in events if e.get('venue') == 'amm']
    
    print(f"📊 Found {len(oanda_orders)} OANDA orders")
    print(f"📊 Found {len(amm_trades)} AMM trades")
    print()
    
    # Try to match by symbol and timestamp proximity
    for oanda_order in oanda_orders:
        symbol = oanda_order.get('symbol')
        timestamp = oanda_order.get('timestamp')
        
        if not symbol or not timestamp:
            continue
        
        # Find matching AMM trade
        for amm_trade in amm_trades:
            if amm_trade.get('symbol') == symbol:
                # Calculate time difference
                try:
                    oanda_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    amm_time = datetime.fromisoformat(amm_trade.get('timestamp', '').replace('Z', '+00:00'))
                    time_diff = abs((amm_time - oanda_time).total_seconds())
                    
                    # If within 60 seconds, consider it a match
                    if time_diff < 60:
                        mappings.append({
                            'oanda_order': oanda_order,
                            'amm_trade': amm_trade,
                            'time_diff_seconds': time_diff
                        })
                        break
                except:
                    continue
    
    return mappings


def print_mappings(mappings: List[Dict[str, Any]]):
    """Print the mappings in a readable format"""
    if not mappings:
        print("❌ No mappings found")
        return
    
    print(f"✅ Found {len(mappings)} OANDA → AMM mappings:")
    print("=" * 80)
    
    for i, mapping in enumerate(mappings, 1):
        oanda = mapping['oanda_order']
        amm = mapping['amm_trade']
        time_diff = mapping['time_diff_seconds']
        
        print(f"\n{i}. {oanda.get('symbol')}")
        print(f"   OANDA: {oanda.get('event_type')} at {oanda.get('timestamp')}")
        print(f"   AMM:   {amm.get('event_type')} at {amm.get('timestamp')}")
        print(f"   Time difference: {time_diff:.1f}s")
        
        # Show details if available
        oanda_details = oanda.get('details', {})
        amm_details = amm.get('details', {})
        
        if 'price' in oanda_details:
            print(f"   Price: {oanda_details.get('price')}")
        if 'pnl' in amm_details:
            print(f"   PnL: ${amm_details.get('pnl'):.2f}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_map_oanda_to_amm.py <narration_file>")
        print("Example: python3 test_map_oanda_to_amm.py narration.jsonl")
        sys.exit(1)
    
    narration_file = sys.argv[1]
    
    print("=" * 80)
    print("OANDA to AMM Mapper")
    print("=" * 80)
    print(f"Loading: {narration_file}")
    print()
    
    # Load events
    events = load_narration_events(narration_file)
    
    if not events:
        print("❌ No events loaded")
        sys.exit(1)
    
    print(f"✅ Loaded {len(events)} total events")
    print()
    
    # Map OANDA to AMM
    mappings = map_oanda_to_amm(events)
    
    # Print results
    print_mappings(mappings)
    
    sys.exit(0 if mappings else 1)
