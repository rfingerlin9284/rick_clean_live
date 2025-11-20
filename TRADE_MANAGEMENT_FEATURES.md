# Trade Management Features - Documentation

## Overview

This document describes the trade management enhancements implemented to address position closing, TP/SL enforcement, and pair management requirements.

## Features Implemented

### 1. TP/SL Validation and Enforcement

**Purpose**: Ensure all trades have Take Profit and Stop Loss set before execution.

**Implementation**:
- `_validate_tp_sl_set()` method validates TP and SL are set and in correct direction
- `calculate_stop_take_levels()` includes null checks and raises errors if calculation fails
- Validation occurs before order submission in `place_trade()`
- All validations are logged to narration.jsonl

**Configuration**:
```python
self.stop_loss_pips = 20      # Default: 20 pips
self.take_profit_pips = 64    # Default: 64 pips (3.2:1 R:R)
```

**Validation Rules**:
- For BUY orders: SL must be < Entry < TP
- For SELL orders: TP < Entry < SL
- Both SL and TP must be non-null
- R:R ratio must meet charter minimum (3.2:1)

### 2. Platform Pair Limits

**Purpose**: Limit trading to 3-4 pairs per platform to manage risk exposure.

**Implementation**:
- `max_pairs_per_platform = 4` (configurable)
- `active_pairs` set tracks currently traded pairs on this platform
- `_can_trade_pair()` checks pair limits before allowing new trades
- Pairs automatically added when positions open
- Pairs automatically removed when positions close

**Usage**:
```python
# Check if pair can be traded
can_trade, reason = self._can_trade_pair(symbol)
if not can_trade:
    # Trade rejected due to pair limits
    print(f"Rejected: {reason}")
```

### 3. Cross-Platform Pair Deduplication

**Purpose**: Prevent the same pair from being traded on multiple platforms simultaneously.

**Implementation**:
- Global pair tracker at `/tmp/rick_trading_global_pairs.json`
- `_load_global_active_pairs()` reads active pairs from all platforms
- `_save_global_active_pairs()` updates global state when pairs change
- Automatic synchronization on position open/close

**Global Tracker Format**:
```json
{
  "pairs": ["EUR_USD", "BTC-USD", "AAPL"],
  "by_broker": {
    "oanda": ["EUR_USD"],
    "coinbase": ["BTC-USD"],
    "ibkr": ["AAPL"]
  },
  "timestamp": "2025-11-20T18:55:00Z"
}
```

### 4. Trade Manager Activation Monitoring

**Purpose**: Verify that the trade manager loop is running and actively monitoring positions.

**Implementation**:
- `trade_manager_active` boolean flag
- `trade_manager_last_heartbeat` timestamp updated every 5 seconds
- Activation logged on start, deactivation logged on stop
- Heartbeat provides health monitoring capability

**Monitoring**:
```python
# Check trade manager status
if self.trade_manager_active:
    age = datetime.now(timezone.utc) - self.trade_manager_last_heartbeat
    if age.total_seconds() < 30:
        print("✅ Trade Manager healthy")
    else:
        print("⚠️  Trade Manager heartbeat stale")
```

## Smart Trailing and Momentum Detection

The trade manager loop integrates momentum-based TP cancellation:

1. **Position Age Check**: Only evaluates positions older than 60 seconds
2. **Hive Mind Analysis**: Queries consensus from multiple strategies
3. **Momentum Detection**: Uses battle-tested momentum detector
4. **TP Cancellation**: Cancels TP when strong momentum detected
5. **Adaptive Trailing**: Sets dynamic trailing stop based on profit level

**Trigger Conditions**:
- Hive consensus exceeds 80% confidence threshold, OR
- Momentum detector confirms strong momentum

**Trailing Stop Levels**:
| Profit Level | Trail Distance | Notes |
|--------------|----------------|-------|
| 0-1x ATR | 1.2x ATR | Charter standard |
| 1-2x ATR | 1.0x ATR | Start tightening |
| 2-3x ATR | 0.8x ATR | Tight |
| 3-4x ATR | 0.6x ATR | Very tight |
| 4-5x ATR | 0.5x ATR | Lock profit |
| 5+x ATR | 0.4x ATR | Ultra tight |

## Configuration

### OANDA Trading Engine

```python
# Pair limits
self.max_pairs_per_platform = 4  # Max 4 pairs

# Trade manager settings
self.min_position_age_seconds = 60  # Wait 60s before momentum check
self.hive_trigger_confidence = 0.80  # 80% confidence threshold

# TP/SL settings (immutable per charter)
self.stop_loss_pips = 20
self.take_profit_pips = 64  # 3.2:1 R:R
```

### Multi-Broker Engine

```python
# Cross-platform pair management
self.max_pairs_per_platform = 4
self.active_pairs_by_broker = defaultdict(set)
self.global_active_pairs_file = '/tmp/rick_trading_global_pairs.json'
```

## Usage Examples

### Checking Trade Manager Status

```python
# In trading loop
if not self.trade_manager_active:
    print("⚠️  WARNING: Trade manager not running!")

# Check heartbeat age
age = (datetime.now(timezone.utc) - self.trade_manager_last_heartbeat).total_seconds()
if age > 30:
    print(f"⚠️  Trade manager heartbeat stale: {age}s ago")
```

### Viewing Active Pairs

```python
# Current platform
print(f"Active pairs: {len(self.active_pairs)}/{self.max_pairs_per_platform}")
for pair in self.active_pairs:
    print(f"  - {pair}")

# All platforms (multi-broker)
for broker, pairs in self.active_pairs_by_broker.items():
    print(f"{broker}: {pairs}")
```

### Manual Position Close

When manually closing a position, the system:
1. Removes pair from `active_pairs`
2. Updates global tracker
3. Logs the removal to narration.jsonl

The smart trailing and momentum detection will not affect manually closed positions since they are removed from `active_positions` before the trade manager evaluates them.

## Logging

All events are logged to `narration.jsonl`:

```json
// TP/SL Validation
{
  "event_type": "TP_SL_VALIDATED",
  "symbol": "EUR_USD",
  "direction": "BUY",
  "stop_loss": 1.0800,
  "take_profit": 1.0900,
  "validation": "PASSED"
}

// Pair Limit Rejection
{
  "event_type": "PAIR_LIMIT_REJECTION",
  "symbol": "NZD_USD",
  "reason": "Platform limit reached (4 pairs max)",
  "active_pairs": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"],
  "max_pairs": 4
}

// Trade Manager Activation
{
  "event_type": "TRADE_MANAGER_ACTIVATED",
  "status": "ACTIVE",
  "timestamp": "2025-11-20T18:55:00Z",
  "min_position_age_seconds": 60,
  "hive_trigger_confidence": 0.80
}

// Momentum Detection
{
  "event_type": "MOMENTUM_DETECTED",
  "symbol": "EUR_USD",
  "profit_atr": 2.5,
  "momentum_strength": 1.25,
  "order_id": "12345"
}

// TP Cancellation
{
  "event_type": "TP_CANCEL_ATTEMPT",
  "order_id": "12345",
  "trigger_source": ["Hive", "Momentum"],
  "profit_atr": 2.5
}
```

## Testing

Run the test suite:

```bash
python3 test_trade_management.py
```

This tests:
1. TP/SL validation for BUY and SELL orders
2. Pair limit enforcement (max 4 pairs)
3. Cross-platform deduplication
4. Trade manager activation monitoring

## Troubleshooting

### Why didn't my position use smart trailing?

1. **Position too young**: Trade manager only evaluates positions older than 60 seconds
2. **No momentum detected**: Neither Hive consensus nor momentum detector triggered
3. **Already processed**: TP already cancelled for this position
4. **Trade manager not running**: Check `trade_manager_active` flag

### Why was my trade rejected?

Check narration.jsonl for rejection reason:
- `PAIR_LIMIT_REJECTION`: Too many pairs on this platform
- `CHARTER_VIOLATION`: Didn't meet minimum notional or R:R requirements
- Cross-platform duplicate: Pair already active on another platform

### Global pair tracker not updating

1. Check file exists: `/tmp/rick_trading_global_pairs.json`
2. Check file permissions
3. Check for errors in `_save_global_active_pairs()` calls

## Charter Compliance

All features maintain charter compliance:
- TP/SL enforcement supports OCO requirement
- Pair limits enhance risk management
- Trade manager uses approved momentum detection
- All actions logged for audit trail
- PIN 841921 validated on engine initialization
