# Dynamic Leverage and Scaling System

## Overview

The OANDA Trading Engine now includes a dynamic leverage and scaling system that adjusts position sizes based on confidence levels from multiple sources:
- **Hive Mind Consensus**: Multi-AI analysis providing confidence scores
- **ML Signal Strength**: Machine learning signal quality assessment

## How It Works

### Leverage Multipliers

The system uses the following leverage tiers:

1. **Base Position (1.0x)**
   - No confidence boost
   - Meets Charter minimum ($15,000 notional)
   - Used when confidence signals are weak or unavailable

2. **High Confidence (1.5x)**
   - Triggered by:
     - Hive Mind confidence >= 0.80 (but < 0.90), OR
     - ML signal strength >= 0.75 (but < 0.85)
   - Example: $15k base → $22.5k leveraged position

3. **Very High Confidence (2.0x)**
   - Triggered by:
     - Hive Mind confidence >= 0.90 AND
     - ML signal strength >= 0.85
   - Example: $15k base → $30k leveraged position

4. **Maximum Cap (2.5x)**
   - Safety limit to prevent over-leverage
   - Automatically applied if calculated multiplier exceeds this

### Charter Compliance

All leveraged positions still comply with Charter requirements:
- **Minimum notional**: $15,000 USD (always met)
- **Risk-reward ratio**: 3.2:1 minimum (enforced)
- **Maximum positions**: 3 concurrent
- **Stop loss/Take profit**: Always set (OCO orders)

## Usage

### Automatic Integration

The dynamic leverage system is automatically applied when placing trades. No manual configuration needed.

```python
# In the trading loop:
trade_id = self.place_trade(
    symbol=symbol,
    direction=direction,
    signal_confidence=0.82,      # ML signal confidence
    hive_confidence=0.88          # Hive Mind confidence
)
```

### Manual Calculation

You can also calculate leverage multipliers independently:

```python
multiplier, reason = engine.calculate_dynamic_leverage_multiplier(
    hive_confidence=0.85,
    ml_signal_strength=0.80,
    symbol="EUR_USD"
)
# Returns: (1.5, "High Hive confidence (0.85); High ML signal strength (0.80)")
```

## Examples

### Example 1: Base Position (No Confidence Boost)
```
Symbol: EUR/USD
Entry: 1.0850
Hive Confidence: None
ML Strength: None

Result:
- Multiplier: 1.0x
- Position Size: 13,900 units
- Notional: $15,081.50
- Reason: "Base position (no confidence boost)"
```

### Example 2: High Hive Confidence
```
Symbol: EUR/USD
Entry: 1.0850
Hive Confidence: 0.85
ML Strength: None

Result:
- Multiplier: 1.5x
- Position Size: 20,900 units
- Notional: $22,676.50
- Reason: "High Hive confidence (0.85)"
```

### Example 3: Combined Very High Confidence
```
Symbol: USD/JPY
Entry: 149.50
Hive Confidence: 0.92
ML Strength: 0.88

Result:
- Multiplier: 2.0x
- Position Size: 2,200 units
- Notional: $328,900.00
- Reason: "Combined very high confidence (Hive: 0.92, ML: 0.88)"
```

## Benefits

1. **Risk-Optimized**: Scale up positions when confidence is high
2. **Capital Efficient**: Maximize returns on high-probability setups
3. **Automated**: No manual intervention required
4. **Safe**: Charter compliance and safety caps enforced
5. **Transparent**: All leverage decisions logged to narration.jsonl

## Monitoring

All leverage decisions are logged to `narration.jsonl` with event type `DYNAMIC_LEVERAGE_CALCULATED`:

```json
{
  "event_type": "DYNAMIC_LEVERAGE_CALCULATED",
  "symbol": "EUR_USD",
  "multiplier": 1.5,
  "hive_confidence": 0.85,
  "ml_signal_strength": null,
  "reason": "High Hive confidence (0.85)",
  "timestamp": "2025-11-20T21:09:00Z"
}
```

## Testing

Run the test suite to verify the dynamic leverage system:

```bash
python3 test_dynamic_leverage.py
```

This runs 10 test cases covering:
- Base multiplier calculations
- High confidence scenarios
- Combined confidence scenarios
- Invalid input handling
- Position sizing with leverage
- Charter compliance verification

## Integration with Existing Features

### Hive Mind
- Queries multiple AI agents (GPT, Grok, DeepSeek)
- Generates consensus confidence score
- Automatically integrated into trading loop

### ML Intelligence
- Regime detection (trending, ranging, volatile)
- Signal quality analysis
- Strength scoring based on market conditions

### Trade Manager
- Still monitors positions for momentum
- Converts TP to trailing stops when appropriate
- Works seamlessly with leveraged positions

### Guardian Gates
- Pre-trade validation still enforced
- Margin correlation checks applied
- Auto-cancellation if gates reject

## Future Enhancements

Potential improvements for future iterations:
1. Per-symbol leverage limits based on volatility
2. Time-of-day leverage adjustments
3. Win-rate based leverage scaling
4. Portfolio-wide leverage limits
5. Backtesting leverage strategies

---

**Charter Compliance**: PIN 841921 | Version 2.0_IMMUTABLE
**Last Updated**: 2025-11-20
