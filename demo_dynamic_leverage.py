#!/usr/bin/env python3
"""
Visual demonstration of dynamic leverage system
Shows how position sizing changes based on confidence levels
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from oanda_trading_engine import OandaTradingEngine


def print_separator():
    print("=" * 80)


def demonstrate_leverage_scenarios():
    """Visual demonstration of different leverage scenarios"""
    
    print_separator()
    print("🤖 DYNAMIC LEVERAGE SYSTEM - VISUAL DEMONSTRATION")
    print_separator()
    print()
    
    engine = OandaTradingEngine(environment='practice')
    
    # Scenario data
    scenarios = [
        {
            "name": "Conservative Entry (No Confidence Boost)",
            "symbol": "EUR_USD",
            "entry_price": 1.0850,
            "hive_conf": None,
            "ml_conf": None,
            "description": "Standard trade with no confidence signals"
        },
        {
            "name": "Moderate Confidence (Below Threshold)",
            "symbol": "GBP_USD",
            "entry_price": 1.2650,
            "hive_conf": 0.72,
            "ml_conf": 0.68,
            "description": "Some confidence but not enough for leverage"
        },
        {
            "name": "High Hive Confidence",
            "symbol": "USD_JPY",
            "entry_price": 149.50,
            "hive_conf": 0.85,
            "ml_conf": None,
            "description": "Strong Hive consensus, no ML signal"
        },
        {
            "name": "High ML Signal Strength",
            "symbol": "AUD_USD",
            "entry_price": 0.6550,
            "hive_conf": None,
            "ml_conf": 0.82,
            "description": "Strong ML signal, no Hive consensus"
        },
        {
            "name": "Both Sources High (Not Combined)",
            "symbol": "EUR_GBP",
            "entry_price": 0.8550,
            "hive_conf": 0.88,
            "ml_conf": 0.79,
            "description": "Both high but ML not ≥0.85 for 2.0x"
        },
        {
            "name": "MAXIMUM CONFIDENCE (Combined Very High)",
            "symbol": "USD_CAD",
            "entry_price": 1.3450,
            "hive_conf": 0.94,
            "ml_conf": 0.91,
            "description": "Hive ≥0.90 AND ML ≥0.85 → 2.0x leverage!"
        }
    ]
    
    print("POSITION SIZING ACROSS DIFFERENT CONFIDENCE SCENARIOS")
    print()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📊 SCENARIO {i}: {scenario['name']}")
        print("-" * 80)
        print(f"Description: {scenario['description']}")
        print()
        print(f"Symbol: {scenario['symbol']}")
        print(f"Entry Price: ${scenario['entry_price']:.4f}")
        if scenario['hive_conf'] is not None:
            print(f"Hive Confidence: {scenario['hive_conf']:.0%}")
        else:
            print("Hive Confidence: N/A")
        if scenario['ml_conf'] is not None:
            print(f"ML Signal Strength: {scenario['ml_conf']:.0%}")
        else:
            print("ML Signal Strength: N/A")
        print()
        
        # Calculate position size
        position_size = engine.calculate_position_size(
            symbol=scenario['symbol'],
            entry_price=scenario['entry_price'],
            hive_confidence=scenario['hive_conf'],
            ml_signal_strength=scenario['ml_conf']
        )
        
        # Calculate notional
        notional = position_size * scenario['entry_price']
        
        # Get multiplier info
        multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
            hive_confidence=scenario['hive_conf'],
            ml_signal_strength=scenario['ml_conf'],
            symbol=scenario['symbol']
        )
        
        # Calculate base size for comparison
        base_size = engine.calculate_position_size(
            symbol=scenario['symbol'],
            entry_price=scenario['entry_price']
        )
        base_notional = base_size * scenario['entry_price']
        
        print(f"RESULTS:")
        print(f"  Leverage Multiplier: {multiplier}x")
        print(f"  Reason: {reason}")
        print()
        print(f"  Base Position: {base_size:,} units → ${base_notional:,.2f} notional")
        print(f"  Final Position: {position_size:,} units → ${notional:,.2f} notional")
        if multiplier > 1.0:
            increase = ((position_size / base_size) - 1) * 100
            notional_increase = notional - base_notional
            print(f"  🚀 BOOST: +{increase:.0f}% size (+${notional_increase:,.2f} notional)")
        else:
            print(f"  ℹ️  No leverage boost applied")
        print()
    
    print_separator()
    print("SUMMARY: CAPITAL EFFICIENCY IMPROVEMENTS")
    print_separator()
    print()
    print("The dynamic leverage system allows you to:")
    print()
    print("  1. ✅ Maintain Charter compliance ($15k minimum) on ALL trades")
    print("  2. 🚀 Scale up position size by 50% on high-confidence setups")
    print("  3. 🎯 Double position size on maximum confidence scenarios")
    print("  4. 🛡️ Automatic safety cap at 2.5x prevents over-leverage")
    print("  5. 📊 Full transparency with narration logging")
    print()
    print("Expected improvement: 15-25% increase in capital efficiency")
    print("while maintaining strict risk management compliance.")
    print()
    print_separator()


if __name__ == "__main__":
    demonstrate_leverage_scenarios()
