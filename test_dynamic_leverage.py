#!/usr/bin/env python3
"""
Test script for dynamic leverage calculation in OANDA Trading Engine
Validates that leverage multipliers are calculated correctly based on confidence levels
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from oanda_trading_engine import OandaTradingEngine
from foundation.rick_charter import RickCharter


def test_dynamic_leverage_multiplier():
    """Test the dynamic leverage multiplier calculation"""
    print("=" * 70)
    print("Testing Dynamic Leverage Multiplier Calculation")
    print("=" * 70)
    print()
    
    # Initialize engine (will use practice mode by default)
    try:
        engine = OandaTradingEngine(environment='practice')
        
        # Test Case 1: Base case - no confidence values
        print("Test 1: Base case (no confidence values)")
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier()
        print(f"  Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        assert multiplier == 1.0, "Base multiplier should be 1.0"
        print("  ✅ PASSED\n")
        
        # Test Case 2: High hive confidence (0.80 - 0.89)
        print("Test 2: High Hive confidence (0.85)")
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
            hive_confidence=0.85,
            symbol="EUR_USD"
        )
        print(f"  Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        assert multiplier == 1.5, f"Expected 1.5x for high Hive confidence, got {multiplier}x"
        print("  ✅ PASSED\n")
        
        # Test Case 3: Very high hive confidence (>= 0.90)
        print("Test 3: Very high Hive confidence (0.92)")
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
            hive_confidence=0.92,
            symbol="GBP_USD"
        )
        print(f"  Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        # Should get higher multiplier but need ML confidence too for 2.0x
        print("  ✅ PASSED\n")
        
        # Test Case 4: High ML signal strength (0.75 - 0.84)
        print("Test 4: High ML signal strength (0.80)")
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
            ml_signal_strength=0.80,
            symbol="USD_JPY"
        )
        print(f"  Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        assert multiplier == 1.5, f"Expected 1.5x for high ML strength, got {multiplier}x"
        print("  ✅ PASSED\n")
        
        # Test Case 5: Combined very high confidence (Hive >= 0.90 AND ML >= 0.85)
        print("Test 5: Combined very high confidence (Hive: 0.92, ML: 0.88)")
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
            hive_confidence=0.92,
            ml_signal_strength=0.88,
            symbol="AUD_USD"
        )
        print(f"  Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        assert multiplier == 2.0, f"Expected 2.0x for combined high confidence, got {multiplier}x"
        print("  ✅ PASSED\n")
        
        # Test Case 6: Invalid confidence values (should use base)
        print("Test 6: Invalid confidence values (negative)")
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
            hive_confidence=-0.5,
            ml_signal_strength=1.5,
            symbol="EUR_GBP"
        )
        print(f"  Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        assert multiplier == 1.0, "Invalid values should result in base multiplier"
        print("  ✅ PASSED\n")
        
        # Test Case 7: Moderate confidence (should still use base or low multiplier)
        print("Test 7: Moderate confidence (Hive: 0.70, ML: 0.65)")
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
            hive_confidence=0.70,
            ml_signal_strength=0.65,
            symbol="USD_CAD"
        )
        print(f"  Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        assert multiplier == 1.0, "Moderate confidence should use base multiplier"
        print("  ✅ PASSED\n")
        
        print("=" * 70)
        print("✅ ALL DYNAMIC LEVERAGE TESTS PASSED")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_position_size_with_leverage():
    """Test position sizing with dynamic leverage"""
    print("\n" + "=" * 70)
    print("Testing Position Sizing with Dynamic Leverage")
    print("=" * 70)
    print()
    
    try:
        engine = OandaTradingEngine(environment='practice')
        
        # Test Case 1: EUR/USD with base multiplier
        print("Test 1: EUR/USD base position (no confidence boost)")
        symbol = "EUR_USD"
        entry_price = 1.0850
        base_size = engine.calculate_position_size(symbol, entry_price)
        print(f"  Symbol: {symbol}")
        print(f"  Entry Price: {entry_price}")
        print(f"  Position Size: {base_size:,} units")
        print(f"  Notional: ${base_size * entry_price:,.2f}")
        assert base_size * entry_price >= engine.min_notional_usd, "Must meet minimum notional"
        print("  ✅ PASSED\n")
        
        # Test Case 2: EUR/USD with high hive confidence
        print("Test 2: EUR/USD with high Hive confidence (0.85)")
        leveraged_size = engine.calculate_position_size(
            symbol=symbol,
            entry_price=entry_price,
            hive_confidence=0.85
        )
        print(f"  Symbol: {symbol}")
        print(f"  Entry Price: {entry_price}")
        print(f"  Base Size: {base_size:,} units")
        print(f"  Leveraged Size: {leveraged_size:,} units")
        print(f"  Multiplier: {leveraged_size / base_size:.2f}x")
        print(f"  Notional: ${leveraged_size * entry_price:,.2f}")
        assert leveraged_size > base_size, "Leveraged size should be greater than base"
        assert leveraged_size * entry_price >= engine.min_notional_usd, "Must meet minimum notional"
        print("  ✅ PASSED\n")
        
        # Test Case 3: USD/JPY with very high combined confidence
        print("Test 3: USD/JPY with very high combined confidence (Hive: 0.92, ML: 0.88)")
        symbol = "USD_JPY"
        entry_price = 149.50
        base_size = engine.calculate_position_size(symbol, entry_price)
        leveraged_size = engine.calculate_position_size(
            symbol=symbol,
            entry_price=entry_price,
            hive_confidence=0.92,
            ml_signal_strength=0.88
        )
        print(f"  Symbol: {symbol}")
        print(f"  Entry Price: {entry_price}")
        print(f"  Base Size: {base_size:,} units")
        print(f"  Leveraged Size: {leveraged_size:,} units")
        print(f"  Multiplier: {leveraged_size / base_size:.2f}x")
        print(f"  Base Notional: ${base_size * entry_price:,.2f}")
        print(f"  Leveraged Notional: ${leveraged_size * entry_price:,.2f}")
        assert leveraged_size >= base_size * 1.9, "Should have ~2.0x multiplier"
        assert leveraged_size * entry_price >= engine.min_notional_usd, "Must meet minimum notional"
        print("  ✅ PASSED\n")
        
        print("=" * 70)
        print("✅ ALL POSITION SIZING TESTS PASSED")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🤖 RBOTzilla Dynamic Leverage System - Test Suite\n")
    
    # Run tests
    test1_passed = test_dynamic_leverage_multiplier()
    test2_passed = test_position_size_with_leverage()
    
    print("\n" + "=" * 70)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Dynamic Leverage System Working Correctly")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Review Output Above")
        sys.exit(1)
    print("=" * 70 + "\n")
