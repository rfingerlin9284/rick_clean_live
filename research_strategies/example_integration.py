#!/usr/bin/env python3
"""
Research Strategies Integration Example
Demonstrates how to use the research_strategies package with trading engines
PIN: 841921
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from research_strategies.pack_manager import create_default_pack_manager


def generate_sample_market_data(n_bars=500):
    """Generate realistic sample market data for testing"""
    np.random.seed(42)
    
    # Generate realistic price movement
    close = 100 + np.cumsum(np.random.randn(n_bars) * 0.5)
    high = close + np.abs(np.random.randn(n_bars) * 0.3)
    low = close - np.abs(np.random.randn(n_bars) * 0.3)
    open_ = close + np.random.randn(n_bars) * 0.2
    volume = np.abs(np.random.randn(n_bars) * 1000 + 5000)
    
    # Create timestamps
    start_time = datetime.now() - timedelta(minutes=n_bars * 5)
    dates = pd.date_range(start_time, periods=n_bars, freq='5min')
    
    return pd.DataFrame({
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)


def main():
    """Main integration example"""
    print("=" * 70)
    print("RESEARCH STRATEGIES PACKAGE - INTEGRATION EXAMPLE")
    print("=" * 70)
    print()
    
    # Create pack manager with all strategies
    print("📦 Creating Strategy Pack Manager...")
    manager = create_default_pack_manager()
    
    stats = manager.get_strategy_stats()
    print(f"✅ Registered {stats['total_strategies']} strategies:")
    for name in stats['strategy_names']:
        print(f"   • {name}")
    print()
    
    # Generate sample market data
    print("📊 Generating sample market data (500 bars)...")
    data = generate_sample_market_data(n_bars=500)
    print(f"   Data range: {data.index[0]} to {data.index[-1]}")
    print(f"   Price range: {data['close'].min():.2f} to {data['close'].max():.2f}")
    print()
    
    # Generate consensus signals
    print("🔍 Generating consensus signals from all strategies...")
    signals = manager.generate_consensus_signals(data)
    
    print(f"✅ Generated {len(signals)} consensus signals")
    print()
    
    # Display signal details
    if signals:
        print("📈 Signal Details:")
        print("-" * 70)
        
        for i, signal in enumerate(signals[:5], 1):  # Show first 5
            print(f"\n  Signal #{i}:")
            print(f"    Timestamp:    {signal.timestamp}")
            print(f"    Direction:    {signal.direction}")
            print(f"    Entry Price:  {signal.entry_price:.5f}")
            print(f"    Stop Loss:    {signal.stop_loss:.5f}")
            print(f"    Take Profit:  {signal.take_profit:.5f}")
            print(f"    Risk/Reward:  {signal.risk_reward:.2f}:1")
            print(f"    Confidence:   {signal.consensus_confidence:.2%}")
            print(f"    Strategies:   {', '.join(signal.contributing_strategies)}")
            print(f"    Vote Count:   {signal.signal_count} strategies")
        
        if len(signals) > 5:
            print(f"\n  ... and {len(signals) - 5} more signals")
    else:
        print("ℹ️  No consensus signals found in sample data")
        print("   (This is normal with random data - real market data will generate signals)")
    
    print()
    print("-" * 70)
    
    # Show configuration
    print("\n⚙️  Current Configuration:")
    print(f"   Minimum Confidence:      {stats['min_confidence']:.0%}")
    print(f"   Minimum Strategies:      {stats['min_strategies']}")
    print(f"   Consensus Threshold:     {stats['consensus_threshold']:.0%}")
    print()
    
    # Integration notes
    print("=" * 70)
    print("INTEGRATION NOTES FOR TRADING ENGINES")
    print("=" * 70)
    print("""
To integrate with your trading engine:

1. Import the pack manager:
   from research_strategies.pack_manager import create_default_pack_manager

2. Create the manager:
   manager = create_default_pack_manager()

3. Generate signals with your market data:
   signals = manager.generate_consensus_signals(market_data)

4. Each signal contains:
   - direction: 'LONG' or 'SHORT'
   - entry_price: Recommended entry price
   - stop_loss: Stop loss price
   - take_profit: Take profit price
   - consensus_confidence: Overall confidence (0-1)
   - risk_reward: Risk/reward ratio
   - contributing_strategies: List of strategies that voted

5. Filter signals by confidence:
   high_conf_signals = [s for s in signals if s.consensus_confidence >= 0.70]

6. Adjust consensus parameters as needed:
   manager.set_consensus_parameters(
       min_confidence=0.70,
       min_strategies=3,
       consensus_threshold=0.75
   )

Note: This package does NOT place orders or manage positions.
      It only provides trading signals for your execution engine.
""")
    
    print("=" * 70)
    print("✅ Integration example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
