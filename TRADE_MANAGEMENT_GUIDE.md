# Trade Management Guide

## Overview
This guide explains the trade management features implemented in the OANDA Trading Engine, including take profit (TP) and stop loss (SL) limits, position management, and trade manager verification.

## TP/SL Configuration

### MANDATORY TP/SL Enforcement
All trades **MUST** have both Take Profit and Stop Loss set. This is enforced at the system level through OCO (One-Cancels-Other) orders.

### LONG (BUY) Positions
- **Entry**: Current market price
- **Stop Loss**: -20 pips (below entry price)
- **Take Profit**: +64 pips (above entry price)
- **R:R Ratio**: 3.2:1

**Example:**
```
Entry Price: 1.0850
Stop Loss:   1.0830 (20 pips below)
Take Profit: 1.0914 (64 pips above)
```

### SHORT (SELL) Positions
- **Entry**: Current market price
- **Stop Loss**: +20 pips (above entry price)
- **Take Profit**: -64 pips (below entry price)
- **R:R Ratio**: 3.2:1

**Example:**
```
Entry Price: 1.0850
Stop Loss:   1.0870 (20 pips above)
Take Profit: 1.0786 (64 pips below)
```

## Trade Manager

### Activation and Verification
The Trade Manager is automatically activated when the trading engine starts. You can verify it's running by checking:

1. **Console Output**: Look for "✅ TRADE MANAGER ACTIVATED AND CONNECTED" message
2. **Status Display**: Shows current status, last heartbeat, and configuration
3. **Heartbeat**: Updated every 5 seconds while the trade manager is running

### Trade Manager Features

#### Smart Trailing Stop
- Monitors positions older than 60 seconds
- Uses Hive Mind consensus and Momentum Detector to identify strong trends
- Automatically converts fixed TP to trailing stop when momentum is detected
- Logs all conversions to narration.jsonl for audit trail

#### Manual Position Closure Detection
The system detects when positions are closed manually (e.g., through OANDA web interface):
- Logs manual closures with full details
- Warns that position was closed outside automated TP/SL system
- Maintains audit trail in narration.jsonl

**Why this matters:**
When you manually close a position, it bypasses the smart trailing stop system. The system will log this event so you can review whether manual intervention was necessary.

## Pair Management

### Platform Limits
- **Maximum**: 4 pairs per platform
- **Global Tracking**: Prevents same pair from being active on multiple platforms
- **Configuration File**: `/tmp/rick_trading_global_pairs.json`

### Example Scenario
```
OANDA Platform: EUR_USD, GBP_USD, USD_JPY, AUD_USD (4/4 pairs - limit reached)
Coinbase: BTC-USD, ETH-USD (2/4 pairs - can add 2 more)
IBKR: AAPL, MSFT (2/4 pairs - can add 2 more)

❌ Cannot add EUR_USD to Coinbase (already active on OANDA)
✅ Can add NZD_USD to Coinbase (not active anywhere)
```

## Verification Methods

### Check Trade Manager Status
The trading engine provides methods to verify trade manager status:

```python
# Get full status
status = engine.get_trade_manager_status()
print(status)
# Output:
# {
#   'active': True,
#   'status': 'ACTIVE',
#   'last_heartbeat': '2025-11-20T19:22:15.834922+00:00',
#   'heartbeat_age_seconds': 2.5,
#   'active_positions_count': 3,
#   'tp_sl_config': {
#     'long_buy': {'stop_loss_pips': -20, 'take_profit_pips': 64},
#     'short_sell': {'stop_loss_pips': 20, 'take_profit_pips': -64}
#   }
# }

# Verify connection
is_connected = engine.verify_trade_manager_connected()
# Returns True if active and heartbeat is recent (< 60 seconds)
```

### Monitor Active Positions
```python
# Check positions (detects manual closures)
engine.check_positions()
```

## Narration Logging

All trade management events are logged to `narration.jsonl`:

### Event Types
- `TRADE_MANAGER_ACTIVATED`: Trade manager started
- `TRADE_MANAGER_DEACTIVATED`: Trade manager stopped
- `TP_SL_VALIDATED`: TP/SL validation passed
- `POSITION_MANUALLY_CLOSED_DETECTED`: Position closed outside system
- `TP_CANCEL_ATTEMPT`: TP order cancelled for trailing stop
- `TRAILING_SL_SET`: Trailing stop loss set
- `HIVE_ANALYSIS`: Hive mind consensus analysis
- `MOMENTUM_DETECTED`: Momentum signal detected

### Example Log Entry
```json
{
  "timestamp": "2025-11-20T19:22:15.834922+00:00",
  "event_type": "POSITION_MANUALLY_CLOSED_DETECTED",
  "symbol": "EUR_USD",
  "venue": "oanda",
  "details": {
    "order_id": "12345",
    "symbol": "EUR_USD",
    "direction": "BUY",
    "entry": 1.0850,
    "stop_loss": 1.0830,
    "take_profit": 1.0914,
    "note": "Position closed outside of automated TP/SL system"
  }
}
```

## Charter Compliance

All trade management features comply with RBOTzilla Charter (PIN: 841921):

- ✅ Minimum R:R Ratio: 3.2:1 (exceeds charter minimum)
- ✅ Immutable OCO Orders: All trades have TP and SL
- ✅ Sub-300ms Execution: Tracked and logged
- ✅ Audit Trail: Complete narration logging
- ✅ Position Police: Automated enforcement every 15 minutes

## Testing

Run the comprehensive test suite:
```bash
python3 test_trade_management.py
```

This tests:
1. TP/SL validation for both BUY and SELL
2. Pair limit enforcement (4 pairs max)
3. Cross-platform deduplication
4. Trade manager activation and heartbeat
5. TP/SL configuration for LONG and SHORT positions

## Troubleshooting

### Trade Manager Not Activating
**Symptom**: No "TRADE MANAGER ACTIVATED" message
**Solution**: Check console output for errors. Trade manager starts automatically in `run_trading_loop()`

### Manual Closures Not Detected
**Symptom**: Manually closed positions not logged
**Solution**: Ensure `check_positions()` is being called regularly in the trading loop

### TP/SL Validation Errors
**Symptom**: Orders rejected with "CRITICAL: Stop Loss not set"
**Solution**: Verify `calculate_stop_take_levels()` is being called before order placement

### Pair Limit Exceeded
**Symptom**: "Platform limit reached (4 pairs max)"
**Solution**: Close existing positions or wait for positions to close before opening new ones

## Best Practices

1. **Never close positions manually** unless absolutely necessary - let the system manage TP/SL
2. **Monitor the trade manager heartbeat** - should update every 5 seconds
3. **Review narration logs** regularly to understand system behavior
4. **Test with paper trading** before going live
5. **Verify TP/SL configuration** on startup matches your risk tolerance

## Support

For issues or questions, review:
- Console output for real-time status
- `narration.jsonl` for complete audit trail
- Test suite for validation examples
- This guide for configuration details
