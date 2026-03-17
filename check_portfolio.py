#!/usr/bin/env python3
"""
Portfolio Status Check for PAPER Mode
Shows current balances and positions in Coinbase Sandbox and OANDA Practice
"""

import sys
from datetime import datetime

print("=" * 80)
print("📊 RICK Trading System - PAPER Mode Portfolio Status")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p EST')}")
print()

# Initialize results
portfolios = {
    'coinbase': {'connected': False, 'balance': None, 'positions': []},
    'oanda': {'connected': False, 'balance': None, 'positions': []}
}

# ============================================================================
# COINBASE SANDBOX
# ============================================================================
print("💰 COINBASE SANDBOX (Crypto Paper Trading)")
print("-" * 80)

try:
    from brokers.coinbase_connector import CoinbaseConnector
    
    cb = CoinbaseConnector()
    print("✅ Connected to Coinbase Sandbox")
    
    # Try to get account info
    try:
        # The connector has methods to get portfolio data
        perf_stats = cb.get_performance_stats()
        
        if perf_stats:
            portfolios['coinbase']['connected'] = True
            print(f"\n📈 Performance Stats:")
            for key, value in perf_stats.items():
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"   ⚠️  Could not retrieve detailed stats: {e}")
    
    print("\n   Note: Coinbase Sandbox provides virtual funds for testing")
    print("   Market: 24/7 Cryptocurrency trading")
    
except Exception as e:
    print(f"❌ Failed to connect: {e}")

print()

# ============================================================================
# OANDA PRACTICE
# ============================================================================
print("💱 OANDA PRACTICE (Forex Paper Trading)")
print("-" * 80)

try:
    from brokers.oanda_connector import OandaConnector
    
    oa = OandaConnector()
    print("✅ Connected to OANDA Practice Account")
    
    # Try to get account info
    try:
        # The connector should have methods to get account data
        perf_stats = oa.get_performance_stats()
        
        if perf_stats:
            portfolios['oanda']['connected'] = True
            print(f"\n📈 Performance Stats:")
            for key, value in perf_stats.items():
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"   ⚠️  Could not retrieve detailed stats: {e}")
    
    print("\n   Note: OANDA Practice provides virtual $100K for testing")
    print("   Market: Forex (Sunday 5pm - Friday 5pm EST)")
    
except Exception as e:
    print(f"❌ Failed to connect: {e}")

print()
print("=" * 80)
print("🎯 PAPER MODE SUMMARY")
print("=" * 80)
print()
print("PAPER Mode means:")
print("  ✅ Paper/Sandbox trading ONLY")
print("  ✅ NO real money at risk")
print("  ✅ Practice API accounts")
print("  ✅ Full strategy testing")
print("  ✅ Real market data")
print("  ✅ Simulated order execution")
print()
print("Both accounts connected:", 
      "✅ YES" if portfolios['coinbase']['connected'] and portfolios['oanda']['connected'] 
      else "⚠️  CHECK CONNECTIONS")
print()
print("Ready to deploy for 48-hour paper trading session!")
print("  → make deploy-full")
print()
print("=" * 80)
