# Cloud-Agent Delegation Error Fix

This document describes the fix for cloud-agent delegation errors that were blocking trades in the RICK trading system.

## Problem Description

The trading engine was experiencing several issues:

1. **CHARTER_VIOLATION** messages for trades with insufficient notional value (< $15,000)
2. **BROKER_REGISTRY_BLOCK** events when attempting to trade symbols already in use on other platforms
3. Missing diagnostic tools to understand why trades weren't being placed
4. No cross-platform position tracking to prevent duplicate positions

## Solution Components

### 1. Positions Registry (`util/positions_registry.py`)

A thread-safe and process-safe registry that tracks active positions across multiple trading platforms (OANDA, IBKR, Coinbase).

**Key Features:**
- File-based registry with exclusive locking (prevents race conditions)
- Prevents same symbol from being traded on multiple platforms simultaneously
- Graceful handling of missing or corrupted registry files
- Automatic cleanup of stale positions
- CLI interface for managing positions

**Usage Examples:**

```bash
# List all active positions
python3 util/positions_registry.py --list

# Check if a symbol is available
python3 util/positions_registry.py --check EUR_USD

# Cleanup stale positions (older than 24 hours)
python3 util/positions_registry.py --cleanup

# Filter by platform
python3 util/positions_registry.py --list --platform oanda
```

**Python API:**

```python
from util.positions_registry import PositionsRegistry

registry = PositionsRegistry()

# Check availability
if registry.is_symbol_available('EUR_USD'):
    # Register position
    registry.register_position(
        symbol='EUR_USD',
        platform='oanda',
        order_id='12345',
        direction='BUY',
        notional_usd=15000.0
    )

# Later, unregister when closed
registry.unregister_position('EUR_USD', 'oanda')
```

### 2. Trade Diagnostic Tool (`util/why_no_trade.py`)

Analyzes why trading signals are not resulting in actual trades by checking:
- Charter compliance (notional, R:R ratio, expected PnL)
- Position registry blocks
- Recent charter violations from narration.jsonl

**Usage Examples:**

```bash
# Diagnose single symbol
RICK_DEV_MODE=1 python3 util/why_no_trade.py --symbol EUR_USD

# Diagnose multiple symbols
RICK_DEV_MODE=1 python3 util/why_no_trade.py --symbols EUR_USD,GBP_USD,USD_JPY

# Verbose output with details
python3 util/why_no_trade.py --symbol EUR_USD --verbose

# JSON output for scripting
python3 util/why_no_trade.py --symbols EUR_USD --json
```

**Output Example:**

```
============================================================
Diagnostic Report: EUR_USD
============================================================
Primary Reason: BROKER_REGISTRY_BLOCK
Message: Symbol EUR_USD already in use on oanda

Registry Status:
{
  "blocked": true,
  "reason": "SYMBOL_ALREADY_IN_USE",
  "details": {
    "platform": "oanda",
    "order_id": "12345",
    "direction": "BUY"
  }
}
```

### 3. Trading Engine Integration

The positions registry has been integrated into `oanda_trading_engine.py`:

**Changes Made:**

1. **Initialization**: Registry is initialized when the engine starts
2. **Pre-Trade Check**: Before placing an order, the engine checks if the symbol is available
3. **Position Registration**: When an order is successfully placed, it's registered in the registry
4. **Position Unregistration**: When a position is closed, it's removed from the registry

**Flow Diagram:**

```
Trade Signal Generated
        ↓
Check Pair Limit (max 3-4 per platform)
        ↓
Check Registry (symbol available?)  ← NEW
        ↓
Get Market Price
        ↓
Charter Compliance Checks
        ↓
Place Order
        ↓
Register Position in Registry  ← NEW
        ↓
Monitor Position
        ↓
Position Closed
        ↓
Unregister from Registry  ← NEW
```

## Testing

### Unit Tests

**Positions Registry Tests** (`tests/test_positions_registry.py`):
- 15 comprehensive test cases
- Tests registration, unregistration, availability checks
- Tests error handling (missing files, corrupted data)
- Tests edge cases (special characters, concurrent access)

**Why No Trade Tests** (`tests/test_why_no_trade.py`):
- 10 test cases covering all diagnostic functionality
- Tests charter compliance checking
- Tests registry block detection
- Tests narration log analysis

**Run Tests:**

```bash
# Run positions registry tests
PYTHONPATH=/home/runner/work/rick_clean_live/rick_clean_live python3 tests/test_positions_registry.py

# Run diagnostic tool tests
PYTHONPATH=/home/runner/work/rick_clean_live/rick_clean_live python3 tests/test_why_no_trade.py

# All tests should pass
```

### Demo Script

A demonstration script (`demo_positions_registry.py`) shows the registry in action:

```bash
python3 demo_positions_registry.py
```

This demonstrates:
- Preventing duplicate positions across platforms
- Tracking positions per platform
- Thread-safe operations
- Graceful error handling

## Verification Commands

Run these commands to verify the fix (from the original issue):

```bash
# 1. Check compilation
python3 -m py_compile util/positions_registry.py && echo 'OK compile' || echo 'PY compile error'

# 2. Run unit tests
PYTHONPATH=/home/runner/work/rick_clean_live/rick_clean_live python3 tests/test_positions_registry.py

# 3. Run diagnostic tool
RICK_DEV_MODE=1 python3 util/why_no_trade.py --symbols EUR_USD,GBP_USD,USD_JPY

# 4. Check registry file
cat /tmp/rick_positions_registry.json || echo 'No registry file present'

# 5. List active positions
python3 util/positions_registry.py --list
```

## Charter Violations Addressed

### MIN_NOTIONAL_PRE_ORDER

The diagnostic tool now clearly identifies when trades are blocked due to insufficient notional value:

```json
{
  "type": "MIN_NOTIONAL_VIOLATION",
  "notional_usd": 9770.18,
  "min_required_usd": 15000,
  "message": "Notional $9,770.18 < $15,000"
}
```

This helps developers understand exactly why the charter is blocking the trade and adjust position sizing accordingly.

### BROKER_REGISTRY_BLOCK

The new registry system prevents trades when a symbol is already active on another platform:

```json
{
  "event_type": "BROKER_REGISTRY_BLOCK",
  "symbol": "EUR_USD",
  "details": {
    "reason": "Symbol already has active position on another platform",
    "active_positions": {...}
  }
}
```

This prevents conflicts and ensures clean position management across multiple brokers.

## Files Changed/Created

### New Files:
- `util/positions_registry.py` - Position tracking registry
- `util/why_no_trade.py` - Trade diagnostic tool
- `tests/test_positions_registry.py` - Registry unit tests
- `tests/test_why_no_trade.py` - Diagnostic tool unit tests
- `demo_positions_registry.py` - Demo script
- `CLOUD_AGENT_DELEGATION_FIX.md` - This documentation

### Modified Files:
- `oanda_trading_engine.py` - Integrated positions registry

## Next Steps

1. **Monitor Production**: Watch for BROKER_REGISTRY_BLOCK events in narration.jsonl
2. **Adjust Position Sizing**: Use diagnostic tool to ensure all positions meet charter requirements
3. **Cross-Platform Coordination**: Ensure all trading engines (OANDA, IBKR, Coinbase) use the same registry file
4. **Periodic Cleanup**: Run registry cleanup regularly to remove stale positions

## Maintenance

### Registry File Location

The registry file is stored at `/tmp/rick_positions_registry.json` by default. For production use, consider:

1. Using a persistent location (not /tmp which may be cleared on reboot)
2. Setting up regular backups
3. Monitoring file size and implementing rotation if needed

### Stale Position Cleanup

Run periodic cleanup to remove positions that weren't properly closed:

```bash
# Remove positions older than 24 hours
python3 util/positions_registry.py --cleanup

# Or use Python API with custom age threshold
from util.positions_registry import PositionsRegistry
registry = PositionsRegistry()
count = registry.cleanup_stale_positions(max_age_hours=6)  # 6 hours for charter compliance
```

## Troubleshooting

### "No registry file present"

This is normal on first run. The registry file is created automatically when the first position is registered.

### "Could not acquire registry lock"

This indicates a timeout while trying to acquire the file lock. Possible causes:
- Another process is holding the lock
- Stale lock file from a crashed process

**Solution**: Remove the lock file manually:
```bash
rm /tmp/rick_positions_registry.json.lock
```

### Tests fail with "Registry file corrupted"

The registry gracefully handles corrupted files by creating a new empty registry. If you see this in tests, it's expected behavior being tested. In production, check the registry file for corruption and restore from backup if needed.

## Summary

This fix provides:
- ✅ Cross-platform position tracking to prevent duplicate trades
- ✅ Clear diagnostic messages explaining why trades are blocked
- ✅ Charter compliance validation before order placement
- ✅ Thread-safe, process-safe registry implementation
- ✅ Comprehensive test coverage (25 tests, all passing)
- ✅ CLI tools for monitoring and management
- ✅ Integration with existing trading engine

All acceptance criteria from the original issue have been met.
