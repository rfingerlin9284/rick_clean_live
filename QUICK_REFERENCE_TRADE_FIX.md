# Quick Reference: Trade Placement Fix

## What Was Fixed
✅ Trading engine now places new trades continuously  
✅ Multiple trades across different currency pairs work  
✅ Positions are automatically cleaned up when closed  
✅ Pair rotation works as intended (max 4 pairs per platform)

## How It Works Now

### Automatic Position Cleanup
Every trading cycle (every 5 minutes by default), the system:
1. Queries OANDA API for open trades
2. Compares with locally tracked positions
3. Removes any positions that have closed
4. Frees up pairs for new trades

### Status Monitoring
The trading loop now shows:
```
Current Status: Active positions: 2/3 | Active pairs: 2/4 | Pairs: ['EUR_USD', 'GBP_USD']
```

This helps you see:
- How many positions are currently open
- Which pairs are active
- Available capacity for new trades

### Pair Limit Enforcement
- Maximum 4 currency pairs per platform
- System pre-checks limits before scanning for signals
- Skips pairs that would violate limits
- Shows clear messages when limits are reached

## Testing Your System

### Run the Test Suite
```bash
cd /home/runner/work/rick_clean_live/rick_clean_live
python3 test_position_cleanup.py
```

Expected output:
```
✅ Test passed: check_positions correctly removes closed positions
✅ Test passed: Can trade new pair when under limit
✅ Test passed: Cannot trade new pair when at limit
✅ Test passed: Can retrade existing pair even at limit
```

### Monitor the Engine
When running the trading engine, watch for these logs:
- `✅ Position closed - Pair XXX_YYY removed from active pairs` - Position cleanup working
- `Current Status: Active positions: X/3` - Position tracking working
- `⚠️ Position limit reached` - At capacity, waiting for positions to close

## What Changed

### File: oanda_trading_engine.py
**Lines 1186-1251**: New `check_positions()` implementation
- Queries OANDA API for open trades
- Cleans up closed positions
- Updates all tracking structures

**Lines 1606-1665**: Enhanced trading loop
- Shows current status
- Pre-checks pair limits
- Better error messages

### New Files
- `test_position_cleanup.py` - Comprehensive test suite
- `TRADE_PLACEMENT_FIX_SUMMARY.md` - Detailed documentation

## Troubleshooting

### If trades still not placing:
1. Check the logs for `Current Status` - are positions actually closing?
2. Verify OANDA API credentials are valid
3. Check if pairs are being blocked by pair limits
4. Look for `PAIR_LIMIT_BLOCKED` or `GATE_REJECTION` in narration.jsonl

### If positions not cleaning up:
1. Verify `get_trades()` is working (check for API errors)
2. Ensure `check_positions()` is being called in the trading loop
3. Check narration.jsonl for `POSITION_CLOSED_DETECTED` events

## Key Metrics to Watch

In `narration.jsonl`, look for these events:
- `POSITION_CLOSED_DETECTED` - Position cleanup triggered
- `TRADE_OPENED` - New trade placed successfully
- `PAIR_LIMIT_REJECTION` - Trade blocked by pair limit
- `GATE_REJECTION` - Trade blocked by risk management

## Next Steps

The system is now ready for continuous operation. You should see:
1. Trades being placed when signals are found
2. Positions closing when TP/SL hit
3. New trades being placed after positions close
4. Proper rotation across currency pairs

## Support

If you encounter issues:
1. Check `narration.jsonl` for detailed logs
2. Review the test results
3. Verify OANDA API connectivity
4. Check that Charter requirements are met ($15k min notional, 3.2:1 R:R)

---
**Note**: This fix is essential for continuous trading operation. The `check_positions()` method must remain functional to prevent position tracking from becoming stale.
