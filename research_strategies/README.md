# Research Strategies Package

Advanced trading strategies with regime awareness and consensus-based signal generation.

**PIN: 841921** | **Version: 1.0.0**

## 📦 Package Structure

```
research_strategies/
├── __init__.py                      # Package initialization
├── indicators.py                    # Technical indicators library
├── patterns.py                      # Price action pattern detection
├── regime_features.py               # Market regime classification
├── trap_reversal_scalper.py         # Liquidity trap reversal strategy
├── ema_scalper.py                   # EMA crossover scalping
├── price_action_holy_grail.py       # Consolidation + engulfing patterns
├── fib_confluence.py                # Fibonacci retracement trading
├── pack_manager.py                  # Strategy aggregation & voting
└── example_integration.py           # Integration example
```

## 🚀 Quick Start

```python
from research_strategies.pack_manager import create_default_pack_manager

# Create manager with all strategies
manager = create_default_pack_manager()

# Generate consensus signals from market data
signals = manager.generate_consensus_signals(market_data)

# Filter by confidence
high_confidence_signals = [
    s for s in signals 
    if s.consensus_confidence >= 0.70
]

# Use signals with trading engine
for signal in high_confidence_signals:
    print(f"{signal.direction} at {signal.entry_price}")
    print(f"SL: {signal.stop_loss}, TP: {signal.take_profit}")
    print(f"Confidence: {signal.consensus_confidence:.2%}")
```

## 📊 Core Modules

### Indicators Module (`indicators.py`)
Technical indicators used across all strategies:

- **RSI** - Relative Strength Index
- **ATR** - Average True Range
- **Bollinger Bands** - Volatility bands
- **MACD** - Moving Average Convergence Divergence
- **EMAs** - Exponential Moving Averages
- **Volume Analysis** - Volume spikes and patterns
- **Swing Points** - Swing high/low identification
- **Momentum** - Price momentum calculation

### Patterns Module (`patterns.py`)
Price action pattern detection:

- **Fair Value Gaps (FVG)** - 3-candle gap detection
- **Consolidation** - Tight range detection
- **Engulfing Patterns** - Bullish/bearish engulfing
- **Liquidity Zones** - Swing-based liquidity identification
- **Break of Structure (BoS)** - Structural breaks
- **Liquidity Sweeps** - False breakout detection

### Regime Features Module (`regime_features.py`)
Market regime classification:

- **Trend Regime** - Bullish/Bearish/Sideways classification
- **Volatility Regime** - Low/Normal/High/Extreme
- **Market Structure** - Higher highs/lows analysis
- **Regime Strength** - Confidence in current regime
- **Breakout Detection** - Consolidation breakout identification

## 🎯 Strategy Modules

### 1. Trap Reversal Scalper
**File**: `trap_reversal_scalper.py`

Detects liquidity traps (false breakouts) and trades the reversal.

**Parameters**:
- ATR period: 14
- RSI period: 14
- Volume spike threshold: 1.5x
- Min risk/reward: 2.0:1
- Position risk: 2% max

**Logic**:
1. Identify liquidity zones (swing highs/lows)
2. Detect sweeps through zones
3. Confirm with RSI extremes (< 30 or > 70)
4. Confirm with volume spike (> 1.5x average)
5. Enter on reversal with 2:1 R:R minimum

### 2. EMA Scalper
**File**: `ema_scalper.py`

Trades EMA 50/200 crossovers with tight stops for quick scalps.

**Parameters**:
- EMA Fast: 50
- EMA Slow: 200
- Stop Loss: 0.3%
- Take Profit: 0.6%
- Risk/Reward: 2.0:1
- Min EMA separation: 0.1%

**Logic**:
1. Detect EMA 50/200 crossovers
2. Require 2-bar confirmation
3. Enter on crossover with tight stops
4. Use fixed percentage stops/targets

### 3. Price Action Holy Grail
**File**: `price_action_holy_grail.py`

Combines consolidation breakouts with engulfing patterns.

**Parameters**:
- Consolidation bars: 10
- Tight range: < 0.5%
- Min body ATR: 0.1
- Volume threshold: 1.5x
- Min risk/reward: 2.0:1

**Logic**:
1. Detect tight consolidation (< 0.5% range over 10 bars)
2. Identify engulfing patterns
3. Trigger on breakout with volume
4. Stop loss at consolidation boundary
5. Dynamic TP based on risk/reward

### 4. Fibonacci Confluence
**File**: `fib_confluence.py`

Trades pullbacks to key Fibonacci retracement zones.

**Parameters**:
- Fib lookback: 10 bars
- Fib levels: 50% and 61.8%
- Entry zone: [50%, 61.8%]
- TP multiple: 2.0x
- SL buffer: -15% below swing

**Logic**:
1. Identify swing high/low in 10-bar window
2. Calculate 50% and 61.8% retracement
3. Enter when price pulls back into zone
4. Stop below swing low with buffer
5. Fixed 2:1 risk/reward target

## 🤝 Pack Manager

The `pack_manager.py` module aggregates signals from multiple strategies and provides consensus-based filtering.

### Consensus Requirements

Default configuration:
- **Minimum Confidence**: 60% per strategy
- **Minimum Strategies**: 2 strategies must agree
- **Consensus Threshold**: 65% weighted average

### Usage

```python
from research_strategies.pack_manager import StrategyPackManager

# Create manager
manager = StrategyPackManager(pin=841921)

# Register strategies
manager.register_strategy(strategy1, weight=1.0)
manager.register_strategy(strategy2, weight=1.2)

# Generate consensus signals
signals = manager.generate_consensus_signals(market_data)

# Adjust consensus parameters
manager.set_consensus_parameters(
    min_confidence=0.70,
    min_strategies=3,
    consensus_threshold=0.75
)

# Update strategy weights based on performance
manager.update_strategy_weights({
    'TrapReversalScalper': 0.85,  # Performed well
    'EMAScalper': 1.15           # Outperformed
})
```

### Signal Format

All strategies output signals in a standardized format:

```python
@dataclass
class AggregatedSignal:
    timestamp: pd.Timestamp          # When signal was generated
    direction: str                   # 'LONG' or 'SHORT'
    entry_price: float               # Recommended entry
    stop_loss: float                 # Stop loss price
    take_profit: float               # Take profit target
    consensus_confidence: float      # Overall confidence (0-1)
    risk_reward: float               # Risk/reward ratio
    contributing_strategies: List    # Strategies that voted
    strategy_votes: Dict             # Individual confidences
    signal_count: int                # Number of strategies
    avg_confidence: float            # Average confidence
```

## 🧪 Testing

Comprehensive test suite with 20 tests covering:
- Indicator calculations
- Pattern detection
- Regime classification
- Strategy signal generation
- Pack manager consensus
- PIN authentication

Run tests:
```bash
python3 -m pytest tests/test_research_strategies_pack_manager.py -v
```

Expected output: **20 passed** ✅

## 📋 Integration Guide

### With Trading Engines

The research_strategies package is designed to integrate with existing trading engines without modifying broker order code.

```python
# 1. Import and create pack manager
from research_strategies.pack_manager import create_default_pack_manager
manager = create_default_pack_manager()

# 2. Get market data (from your existing data feed)
market_data = your_trading_engine.get_market_data()

# 3. Generate signals
signals = manager.generate_consensus_signals(market_data)

# 4. Filter and execute
for signal in signals:
    if signal.consensus_confidence >= 0.70:
        # Use your existing order execution
        your_trading_engine.place_order(
            direction=signal.direction,
            entry=signal.entry_price,
            sl=signal.stop_loss,
            tp=signal.take_profit
        )
```

### With Session Breaker

The package integrates seamlessly with the existing `session_breaker.py`:

```python
from risk.session_breaker import SessionBreakerEngine
from research_strategies.pack_manager import create_default_pack_manager

# Initialize both systems
breaker = SessionBreakerEngine()
manager = create_default_pack_manager()

# Generate signals
signals = manager.generate_consensus_signals(market_data)

# Check session breaker before executing
for signal in signals:
    # Check if trading is allowed
    if breaker.check_breaker(current_pnl, account_balance):
        # Execute signal
        execute_trade(signal)
    else:
        # Session breaker triggered - halt trading
        break
```

## 🛡️ Safety & Guardian Rules

The strategies implement the guardian rules defined in `STRATEGY_PARAMETERS_COMPLETE.md`:

### Position Sizing
- Max 5% per currency pair
- Max 10% total daily risk
- 2% default position risk

### Frequency Controls
- Max 15 signals/hour across all strategies
- Max 100 signals/day
- Strategy-specific limits enforced

### Quality Gates
- Min 60% confidence per strategy
- Require 2+ strategies agreeing
- 65% consensus threshold

### Risk/Reward
- Min 2:1 R:R for all strategies
- ATR-based dynamic stops
- Fixed percentage stops for scalpers

## 🔐 Security

- **PIN Authentication**: All modules require PIN 841921
- **No Broker Access**: Package only generates signals
- **No Order Execution**: Integrates with existing execution engines
- **Immutable Parameters**: Core parameters protected from modification

## 📈 Performance Characteristics

Expected performance (based on strategy design):

| Strategy              | Target Win Rate | R:R Ratio | Trades/Day |
|----------------------|-----------------|-----------|------------|
| Trap Reversal        | 55%+            | 2:1       | 5-15       |
| EMA Scalper          | 45%+            | 2:1       | 10-30      |
| Price Action         | 55%+            | 2:1       | 5-20       |
| Fib Confluence       | 50%+            | 2:1       | 5-15       |

**Note**: Actual performance depends on market conditions and must be validated through paper trading.

## 🚫 What This Package Does NOT Do

- ❌ Place broker orders
- ❌ Manage positions
- ❌ Execute trades
- ❌ Access broker APIs
- ❌ Manage account balance
- ❌ Handle fills/slippage

It **ONLY** provides:
- ✅ Strategy signals
- ✅ Confidence scores
- ✅ Entry/SL/TP recommendations
- ✅ Consensus filtering

## 📝 Example Output

```
📦 Creating Strategy Pack Manager...
✅ Registered 4 strategies:
   • TrapReversalScalper
   • EMAScalper
   • PriceActionHolyGrail
   • FibConfluence

🔍 Generating consensus signals from all strategies...
✅ Generated 12 consensus signals

📈 Signal Details:

  Signal #1:
    Timestamp:    2024-01-15 14:32:45
    Direction:    LONG
    Entry Price:  1.10050
    Stop Loss:    1.10006
    Take Profit:  1.10138
    Risk/Reward:  2.00:1
    Confidence:   72.5%
    Strategies:   TrapReversalScalper, PriceActionHolyGrail
    Vote Count:   2 strategies
```

## 🔧 Configuration

Adjust consensus parameters based on your risk tolerance:

```python
# Conservative (higher quality, fewer signals)
manager.set_consensus_parameters(
    min_confidence=0.70,
    min_strategies=3,
    consensus_threshold=0.75
)

# Aggressive (more signals, lower confidence)
manager.set_consensus_parameters(
    min_confidence=0.55,
    min_strategies=2,
    consensus_threshold=0.60
)

# Balanced (default)
manager.set_consensus_parameters(
    min_confidence=0.60,
    min_strategies=2,
    consensus_threshold=0.65
)
```

## 📚 Additional Resources

- **STRATEGY_PARAMETERS_COMPLETE.md** - Complete parameter reference
- **COMPLETE_STRATEGY_AUDIT_SUMMARY.md** - Strategy audit details
- **example_integration.py** - Working integration example
- **test_research_strategies_pack_manager.py** - Test suite

## ⚠️ Important Notes

1. **Paper Trade First**: Always validate in paper trading before live
2. **Monitor Performance**: Track win rates and adjust weights
3. **Respect Guardian Rules**: Don't bypass safety thresholds
4. **Session Breaker**: Always use with session breaker for risk control
5. **Market Data Quality**: Garbage in = garbage out
6. **No Guarantee**: Past performance doesn't guarantee future results

## 🎉 Ready to Use

The research_strategies package is complete, tested, and ready for integration with your trading systems. See `example_integration.py` for a working demonstration.

**All 20 tests passing ✅**
**PIN 841921 authenticated ✅**
**Integration ready ✅**
