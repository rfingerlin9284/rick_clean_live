# GitHub Copilot Instructions for RICK Trading System

## Project Overview

This is **RICK_LIVE_CLEAN**, a sophisticated live trading system that executes automated trades across multiple brokers (OANDA for FX, Coinbase for crypto) with rigorous risk management and safety controls.

**Core Purpose:** Automated trading system with ML intelligence, multi-mode operation (GHOST/CANARY/LIVE), and immutable charter-based risk controls.

**Key Features:**
- Multi-broker support (OANDA FX, Coinbase crypto)
- Four-mode operation: OFF/GHOST/CANARY/LIVE
- ML-enhanced trading intelligence (pattern learning, regime detection)
- Immutable charter enforcement (PIN: 841921)
- Real-time narration logging and P&L tracking
- Static HTML dashboard with auto-refresh
- Wolfpack strategy orchestration

## Tech Stack

- **Language:** Python 3.x
- **Broker APIs:** 
  - oandapyV20 (OANDA FX)
  - coinbase-advanced-py (Coinbase crypto)
  - ib_insync (Interactive Brokers - optional)
- **Data/ML:** pandas, numpy, scikit-learn
- **Visualization:** Streamlit, static HTML
- **Configuration:** python-dotenv, environment-based configs
- **Testing:** pytest

## System Architecture

### Core Components

1. **Charter (`foundation/rick_charter.py`)**
   - Immutable trading constants with PIN validation (841921)
   - Self-validating on import - NEVER bypass validation
   - Defines: max hold time (6h), min RR (3.2:1), min notional ($15k)

2. **Mode Manager (`util/mode_manager.py`)**
   - Controls OFF/GHOST/CANARY/LIVE modes via `.upgrade_toggle`
   - Auto-detects connector environments (practice/sandbox/live)
   - Requires PIN for LIVE mode switches

3. **Narration Logger (`util/narration_logger.py`)**
   - Append-only event logging to `narration.jsonl`
   - P&L tracking to `pnl.jsonl`
   - Session summary aggregation

4. **Broker Connectors**
   - `brokers/oanda_connector.py` - OANDA FX trading
   - `brokers/coinbase_connector.py` - Coinbase crypto trading
   - Both enforce min-notional ($15k) with auto-upsizing

5. **Progress Tracker (`util/progress_tracker.py`)**
   - Auto-generates README.md from PROGRESS_LOG.json
   - Immutable append-only progress logging
   - Timestamped backups

### Trading Modes

```
OFF     → OANDA: practice, Coinbase: sandbox (safe default)
GHOST   → OANDA: practice, Coinbase: sandbox (45-min validation)
CANARY  → OANDA: practice, Coinbase: sandbox (extended testing)
LIVE    → OANDA: live, Coinbase: live (requires PIN: 841921)
```

## Coding Standards

### General Guidelines

- **Style:** Follow PEP 8 conventions
- **Imports:** Use absolute imports from project root
- **Docstrings:** Use triple-quoted docstrings for modules, classes, and functions
- **Type hints:** Use type hints for function parameters and return values
- **Error handling:** Always use try/except blocks for external API calls
- **Logging:** Use Python's logging module, NOT print statements (except in CLI scripts)

### Naming Conventions

- **Classes:** PascalCase (e.g., `RickCharter`, `OandaConnector`)
- **Functions/Methods:** snake_case (e.g., `validate_pin`, `switch_mode`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `MIN_RISK_REWARD_RATIO`, `PIN`)
- **Files:** snake_case (e.g., `mode_manager.py`, `narration_logger.py`)
- **Private methods:** Prefix with underscore (e.g., `_internal_method`)

### Code Organization

- Keep related functionality together in modules
- Use `foundation/` for core immutable components
- Use `util/` for shared utilities
- Use `brokers/` for connector implementations
- Use `scripts/` for operational scripts and tools
- Use `dashboard/` for monitoring and visualization

## Safety & Security - CRITICAL

### Immutable Charter Rules

- **NEVER modify constants in `foundation/rick_charter.py`**
- **NEVER bypass PIN validation** (841921)
- **NEVER skip charter validation checks**
- System will fail import if charter is tampered with

### Trading Safety

- **ALWAYS validate mode switches** via `mode_manager.switch_mode()`
- **NEVER edit `.upgrade_toggle` directly** - use mode_manager API
- **ALWAYS enforce min-notional** ($15k) in broker connectors
- **ALWAYS log to narration.jsonl** for audit trail
- **NEVER delete or truncate logs** - they are append-only

### Secrets Management

- **NEVER commit API keys or credentials** to the repository
- Use `.env` files (already in `.gitignore`)
- Load environment variables via `python-dotenv`
- Use environment detection (practice/sandbox/live) based on mode

### Code Review Focus Areas

When reviewing code changes:
1. Verify charter compliance (RR ratio ≥ 3.2, hold time ≤ 6h, notional ≥ $15k)
2. Check for hardcoded credentials or API keys
3. Validate error handling for broker API calls
4. Ensure narration logging for all significant events
5. Verify mode switching uses proper PIN validation
6. Check that constants are not modified
7. Ensure tests exist for new trading logic

## Testing Requirements

### Test Coverage

- **Unit tests:** For all utility functions and validators
- **Integration tests:** For broker connectors (use sandbox/practice)
- **System tests:** For mode switching and trading workflows
- Use pytest framework (`pytest` command)

### Test Isolation

- **NEVER run tests against live broker accounts**
- Always use practice/sandbox environments for tests
- Mock external API calls where appropriate
- Use fixtures for test data and configurations

### Verification Commands

Before committing changes:
```bash
# Validate charter imports successfully
python3 -c "from foundation.rick_charter import RickCharter; print('Charter valid ✅')"

# Run test suite
pytest

# Check system status
python3 -c "from util.mode_manager import get_current_mode; print(f'Current mode: {get_current_mode()}')"
```

## Documentation Standards

### Code Documentation

- Every module should have a docstring explaining its purpose
- Every class should document its responsibility
- Every public function should have a docstring with:
  - Brief description
  - Parameters (with types)
  - Return value (with type)
  - Raises (if applicable)

### README Updates

- The main `README.md` is **auto-generated** by `util/progress_tracker.py`
- **NEVER edit README.md manually** - it will be overwritten
- To update progress, use `ProgressTracker.mark_complete()` method
- Manual docs should go in separate markdown files

## Common Patterns

### Connector Usage

```python
from brokers.oanda_connector import OandaConnector

# Auto-detect environment based on current mode
connector = OandaConnector(pin=841921)  # Uses environment=None for auto-detection
```

### Mode Switching

```python
from util.mode_manager import switch_mode

# Switch to GHOST mode (no PIN required)
switch_mode('GHOST')

# Switch to LIVE mode (requires PIN)
switch_mode('LIVE', pin=841921)
```

### Narration Logging

```python
from util.narration_logger import log_narration, log_pnl

# Log trading events
log_narration("TRADE_ENTRY", {"symbol": "EUR_USD", "side": "BUY"})

# Log P&L
log_pnl(gross_pnl=150.0, fees=2.5, net_pnl=147.5, outcome="WIN")
```

### Charter Validation

```python
from foundation.rick_charter import RickCharter

# Validate risk-reward ratio
if not RickCharter.validate_risk_reward(rr_ratio):
    raise ValueError(f"RR ratio {rr_ratio} below minimum {RickCharter.MIN_RISK_REWARD_RATIO}")

# Validate timeframe
if not RickCharter.validate_timeframe("M15"):
    raise ValueError("Invalid timeframe")
```

## Special Considerations

### File Paths

- This repository was migrated from `R_H_UNI` to `RICK_LIVE_CLEAN`
- **ALWAYS use** `RICK_LIVE_CLEAN` in absolute paths
- Never reference `R_H_UNI` paths

### Dependencies

- **NO TA-LIB dependency** - Pure Python implementations provided
- Use pandas/numpy for technical calculations
- Keep dependencies minimal and well-documented in `requirements.txt`

### Progress Tracking

- Use `util/progress_tracker.py` for phase completion tracking
- Creates immutable append-only log in `PROGRESS_LOG.json`
- Auto-generates README with breadcrumb trail
- Creates timestamped backups before updates

## Common Pitfalls to Avoid

1. **Don't bypass charter validation** - System integrity depends on it
2. **Don't use print() for logging** - Use logging module or narration_logger
3. **Don't modify .upgrade_toggle directly** - Use mode_manager API
4. **Don't hardcode broker credentials** - Use environment variables
5. **Don't skip error handling** - All broker API calls can fail
6. **Don't delete logs** - They are append-only audit trails
7. **Don't edit README.md manually** - It's auto-generated
8. **Don't add TA-Lib dependency** - Use pure Python alternatives

## Resources

- Charter enforcement: `foundation/rick_charter.py`
- Mode management: `util/mode_manager.py`
- Logging system: `util/narration_logger.py`
- Progress tracking: `util/progress_tracker.py`
- System status: `.upgrade_toggle` file
- Trading logs: `pre_upgrade/headless/logs/narration.jsonl` and `pnl.jsonl`

## When in Doubt

1. Check if the change violates charter constraints
2. Verify the change doesn't compromise trading safety
3. Ensure proper error handling and logging
4. Add tests for new functionality
5. Use sandbox/practice environments for testing
6. Ask for clarification before modifying core components

---

**Remember:** This is a live trading system handling real money. Code quality, safety, and testing are paramount. When suggesting changes, always prioritize system stability and charter compliance over new features.
