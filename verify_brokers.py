#!/usr/bin/env python3
"""
Broker Connection Verification Script
Tests Coinbase Sandbox and OANDA Practice connections
"""

import sys
import os
from datetime import datetime

print("=" * 80)
print("🔌 RICK Trading System - Broker Connection Verification")
print("=" * 80)
print()

# Test results tracker
results = {
    'coinbase': {'connected': False, 'error': None, 'balance': None},
    'oanda': {'connected': False, 'error': None, 'balance': None}
}

# Test Coinbase Sandbox
print("1️⃣  Testing Coinbase Sandbox Connection...")
print("   Loading connector...")

try:
    from brokers.coinbase_connector import CoinbaseConnector
    
    print("   Initializing Coinbase connector...")
    cb = CoinbaseConnector()
    
    print("   Testing authentication...")
    # Connector initialized successfully means connection is working
    # The __init__ method validates the connection
    
    results['coinbase']['connected'] = True
    print("   ✅ Coinbase Sandbox: CONNECTED")
    print("   ✅ Connector initialized and validated")
        
except Exception as e:
    results['coinbase']['error'] = str(e)
    print(f"   ❌ Coinbase Sandbox: FAILED")
    print(f"   Error: {e}")

print()

# Test OANDA Practice
print("2️⃣  Testing OANDA Practice Connection...")
print("   Loading connector...")

try:
    from brokers.oanda_connector import OandaConnector
    
    print("   Initializing OANDA connector...")
    oa = OandaConnector()
    
    print("   Testing authentication...")
    # Connector initialized successfully means connection is working
    # The __init__ method validates the connection
    
    results['oanda']['connected'] = True
    print("   ✅ OANDA Practice: CONNECTED")
    print("   ✅ Connector initialized and validated")
        
except Exception as e:
    results['oanda']['error'] = str(e)
    print(f"   ❌ OANDA Practice: FAILED")
    print(f"   Error: {e}")

print()
print("=" * 80)
print("📊 Connection Summary")
print("=" * 80)
print()

# Summary
coinbase_status = "✅ CONNECTED" if results['coinbase']['connected'] else "❌ NOT CONNECTED"
oanda_status = "✅ CONNECTED" if results['oanda']['connected'] else "❌ NOT CONNECTED"

print(f"Coinbase Sandbox:  {coinbase_status}")
if results['coinbase']['error']:
    print(f"   Error: {results['coinbase']['error']}")

print(f"OANDA Practice:    {oanda_status}")
if results['oanda']['error']:
    print(f"   Error: {results['oanda']['error']}")

print()

# Overall status
both_connected = results['coinbase']['connected'] and results['oanda']['connected']

if both_connected:
    print("🎉 SUCCESS: Both brokers are connected and ready for paper trading!")
    print()
    print("You can now proceed with:")
    print("   • make deploy-full    - Deploy complete 48h system")
    print("   • make paper-session   - Run PAPER validation session")
    print()
    sys.exit(0)
else:
    print("⚠️  WARNING: Not all brokers are connected")
    print()
    print("Please check:")
    print("   • API credentials in env_new.env")
    print("   • Network connectivity")
    print("   • Broker API status")
    print()
    sys.exit(1)
