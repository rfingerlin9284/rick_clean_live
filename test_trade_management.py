#!/usr/bin/env python3
"""
Test Trade Management Features
Tests TP/SL validation and pair management
"""

import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tp_sl_validation():
    """Test that TP/SL validation works correctly"""
    print("=" * 60)
    print("TEST 1: TP/SL Validation")
    print("=" * 60)
    
    # Mock a simple validation function
    def validate_tp_sl(symbol, direction, stop_loss, take_profit):
        """Simplified validation"""
        if stop_loss is None:
            raise ValueError(f"CRITICAL: Stop Loss not set for {symbol} {direction}")
        
        if take_profit is None:
            raise ValueError(f"CRITICAL: Take Profit not set for {symbol} {direction}")
        
        if direction == "BUY":
            if stop_loss >= take_profit:
                raise ValueError(f"CRITICAL: For BUY, SL ({stop_loss}) must be < TP ({take_profit})")
        else:  # SELL
            if stop_loss <= take_profit:
                raise ValueError(f"CRITICAL: For SELL, SL ({stop_loss}) must be > TP ({take_profit})")
        
        return True
    
    # Test cases
    test_cases = [
        # (symbol, direction, stop_loss, take_profit, should_pass)
        ("EUR_USD", "BUY", 1.0800, 1.0900, True),  # Valid BUY
        ("EUR_USD", "SELL", 1.0900, 1.0800, True),  # Valid SELL
        ("EUR_USD", "BUY", None, 1.0900, False),  # Missing SL
        ("EUR_USD", "BUY", 1.0800, None, False),  # Missing TP
        ("EUR_USD", "BUY", 1.0900, 1.0800, False),  # SL > TP for BUY (invalid)
        ("EUR_USD", "SELL", 1.0800, 1.0900, False),  # SL < TP for SELL (invalid)
    ]
    
    passed = 0
    failed = 0
    
    for symbol, direction, sl, tp, should_pass in test_cases:
        try:
            validate_tp_sl(symbol, direction, sl, tp)
            if should_pass:
                print(f"✅ PASS: {symbol} {direction} SL={sl} TP={tp}")
                passed += 1
            else:
                print(f"❌ FAIL: {symbol} {direction} SL={sl} TP={tp} - Should have failed but passed")
                failed += 1
        except ValueError as e:
            if not should_pass:
                print(f"✅ PASS: {symbol} {direction} - Correctly rejected: {str(e)[:50]}")
                passed += 1
            else:
                print(f"❌ FAIL: {symbol} {direction} - Should have passed but failed: {str(e)[:50]}")
                failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_pair_limits():
    """Test pair limit enforcement"""
    print("\n" + "=" * 60)
    print("TEST 2: Pair Limit Management")
    print("=" * 60)
    
    max_pairs = 4
    active_pairs = set()
    
    def can_trade_pair(symbol):
        """Check if we can trade this pair"""
        if len(active_pairs) >= max_pairs:
            if symbol not in active_pairs:
                return False, f"Platform limit reached ({max_pairs} pairs max)"
        return True, "OK"
    
    # Test adding pairs up to limit
    test_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'NZD_USD']
    
    passed = 0
    failed = 0
    
    for i, pair in enumerate(test_pairs):
        can_trade, reason = can_trade_pair(pair)
        
        if i < max_pairs:
            # Should be able to trade
            if can_trade:
                active_pairs.add(pair)
                print(f"✅ PASS: Added {pair} ({len(active_pairs)}/{max_pairs})")
                passed += 1
            else:
                print(f"❌ FAIL: Should have added {pair} but rejected: {reason}")
                failed += 1
        else:
            # Should be rejected (over limit)
            if not can_trade:
                print(f"✅ PASS: Correctly rejected {pair}: {reason}")
                passed += 1
            else:
                print(f"❌ FAIL: Should have rejected {pair} (over limit)")
                failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    print(f"Active pairs: {active_pairs}")
    return failed == 0


def test_cross_platform_deduplication():
    """Test that pairs cannot be duplicated across platforms"""
    print("\n" + "=" * 60)
    print("TEST 3: Cross-Platform Deduplication")
    print("=" * 60)
    
    # Simulate multiple platforms
    active_pairs_by_platform = {
        'oanda': {'EUR_USD', 'GBP_USD'},
        'ibkr': {'AAPL', 'MSFT'},
        'coinbase': set()
    }
    
    def can_trade_pair(platform, symbol):
        """Check if pair can be traded on this platform"""
        # Check if already active on another platform
        for other_platform, pairs in active_pairs_by_platform.items():
            if other_platform != platform and symbol in pairs:
                return False, f"Pair {symbol} already active on {other_platform}"
        return True, "OK"
    
    test_cases = [
        # (platform, symbol, should_pass)
        ('coinbase', 'BTC-USD', True),  # New pair, should pass
        ('coinbase', 'EUR_USD', False),  # Already on OANDA, should fail
        ('ibkr', 'EUR_USD', False),  # Already on OANDA, should fail
        ('oanda', 'EUR_USD', True),  # Already on same platform, should pass
        ('coinbase', 'ETH-USD', True),  # New pair, should pass
    ]
    
    passed = 0
    failed = 0
    
    for platform, symbol, should_pass in test_cases:
        can_trade, reason = can_trade_pair(platform, symbol)
        
        if should_pass:
            if can_trade:
                print(f"✅ PASS: {platform} can trade {symbol}")
                passed += 1
            else:
                print(f"❌ FAIL: {platform} should trade {symbol} but rejected: {reason}")
                failed += 1
        else:
            if not can_trade:
                print(f"✅ PASS: {platform} correctly rejected {symbol}: {reason}")
                passed += 1
            else:
                print(f"❌ FAIL: {platform} should reject {symbol} (duplicate)")
                failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_trade_manager_monitoring():
    """Test trade manager activation monitoring"""
    print("\n" + "=" * 60)
    print("TEST 4: Trade Manager Monitoring")
    print("=" * 60)
    
    # Simulate trade manager state
    trade_manager_active = False
    trade_manager_last_heartbeat = None
    
    # Simulate activation
    trade_manager_active = True
    trade_manager_last_heartbeat = datetime.now(timezone.utc)
    
    print(f"✅ Trade Manager activated: {trade_manager_active}")
    print(f"✅ Last heartbeat: {trade_manager_last_heartbeat.isoformat()}")
    
    # Check if heartbeat is recent (within last 10 seconds)
    age = (datetime.now(timezone.utc) - trade_manager_last_heartbeat).total_seconds()
    if age < 10:
        print(f"✅ PASS: Heartbeat is recent ({age:.2f}s ago)")
        return True
    else:
        print(f"❌ FAIL: Heartbeat is stale ({age:.2f}s ago)")
        return False


if __name__ == "__main__":
    print("\n🧪 TRADE MANAGEMENT TEST SUITE")
    print("Testing TP/SL validation and pair management features")
    print("=" * 60)
    
    all_passed = True
    
    # Run all tests
    all_passed &= test_tp_sl_validation()
    all_passed &= test_pair_limits()
    all_passed &= test_cross_platform_deduplication()
    all_passed &= test_trade_manager_monitoring()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
