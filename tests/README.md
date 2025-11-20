# IBKR Connector Testing Documentation

## Overview

This directory contains test infrastructure for the Interactive Brokers (IBKR) connector, including mock-based tests that don't require an actual IB Gateway connection.

## Test Files

### 1. `test_ibkr_connector_mock.py`
Comprehensive mock-based tests for the IBConnector class.

**Features:**
- Tests order placement without requiring IB Gateway
- Tests market data retrieval
- Tests account summary functionality
- Uses FakeIB mock class to simulate IB Gateway behavior

**Usage:**
```bash
python3 tests/test_ibkr_connector_mock.py
```

**Tests Included:**
1. **Get Best Bid/Ask** - Verifies market data retrieval for multiple symbols
2. **Place Limit Order** - Tests order placement with stop loss and take profit
3. **Account Summary** - Validates account information retrieval
4. **Error Handling** - Tests handling of invalid symbols and error conditions

### Mock Architecture

The test suite includes a complete mock implementation of the `ib_insync` library:

- **FakeIB**: Simulates IB Gateway connection and API calls
- **MockContract**: Simulates contract objects (Forex, Stock, Future)
- **MockOrder**: Simulates order objects (Market, Limit, Stop)
- **MockTrade**: Simulates trade execution results

### Mock Data

The FakeIB class includes realistic test data:
- EUR.USD: BID=1.0850, ASK=1.0852
- GBP.USD: BID=1.2650, ASK=1.2652
- AAPL: BID=175.50, ASK=175.52
- BTC: BID=42000.0, ASK=42050.0

## Utility Test Scripts

### 2. `util/test_map_oanda_write.py`
Writes test narrations for OANDA orders and AMM trades.

**Usage:**
```bash
python3 util/test_map_oanda_write.py
```

**Purpose:**
- Create test data in narration.jsonl
- Simulate OANDA order placement
- Simulate AMM trade completion

### 3. `util/test_check_engine_status.py`
Checks trading engine health and activity.

**Usage:**
```bash
python3 util/test_check_engine_status.py
```

**Checks:**
- Narration file existence
- Recent activity (last 5 minutes)
- Event type breakdown
- Error detection
- Overall engine health status

### 4. `util/test_map_oanda_to_amm.py`
Maps OANDA orders to AMM trades from narration logs.

**Usage:**
```bash
python3 util/test_map_oanda_to_amm.py narration.jsonl
```

**Features:**
- Loads and parses narration.jsonl
- Matches OANDA orders to AMM trades by symbol and timestamp
- Shows time differences and PnL data

## Running All Tests

```bash
# Run IBKR connector mock tests
python3 tests/test_ibkr_connector_mock.py

# Check engine status
python3 util/test_check_engine_status.py

# Write test narration data
python3 util/test_map_oanda_write.py

# Map OANDA to AMM trades
python3 util/test_map_oanda_to_amm.py narration.jsonl
```

## Error Handling

The IBKR connector includes comprehensive error handling:

### Connection Errors
- Automatic reconnection on connection loss
- Timeout handling (20 seconds default)
- Clear error messages for common issues

### Order Errors
- Validation of order parameters
- Error responses include full context
- Logging of all errors for debugging

### Market Data Errors
- Timeout handling for missing data
- Fallback to safe defaults
- Warning messages for unavailable symbols

## Dependencies

The IBKR connector requires:
```
ib_insync>=0.9.86
```

Install with:
```bash
pip install -r requirements.txt
```

## Testing Without IB Gateway

The mock tests are designed to run without IB Gateway:
- No network connection required
- Instant execution
- Deterministic results
- Safe for CI/CD pipelines

## Integration Testing

For integration testing with actual IB Gateway:
1. Start IB Gateway or TWS
2. Enable API in settings
3. Configure port (4002 for paper, 4001 for live)
4. Set environment variables in `env_new2.env`

## Charter Compliance

All tests maintain charter compliance:
- PIN validation (841921)
- Narration logging
- Capital limits enforced
- Risk management rules

## Troubleshooting

### Test Failures

If tests fail:
1. Check Python version (3.8+)
2. Verify all dependencies installed
3. Check narration.jsonl exists
4. Review error messages in output

### Mock Issues

If mock behavior differs from real IB:
1. Update FakeIB market data
2. Adjust mock order responses
3. Add additional mock scenarios

## Future Enhancements

Potential improvements:
- Add tests for error scenarios
- Test with multiple concurrent orders
- Add performance benchmarking
- Test connection recovery
- Add tests for different asset types

## Contact

For issues or questions about testing:
- Check logs in `logs/` directory
- Review narration.jsonl for event history
- Consult main README.md for system overview
