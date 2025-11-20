# Ghost Trading Configuration Cleanup Scripts

This directory contains utility scripts to clean up ghost trading configurations and establish a clean two-mode system (canary + demo).

## Scripts

### obliterate_ghost_trading.sh

**Purpose**: Safely remove all ghost trading configurations from the repository.

**What it does**:
1. Skips protected directories: ROLLBACK_SNAPSHOTS, .git, .venv, archives
2. Forces ghost/simulation flags OFF in all code files
3. Renames `GHOST_CHARTER` labels to `CANARY_CHARTER`
4. Removes stale ghost progress/log files
5. Ensures `narration.jsonl` exists and is writable

**Usage**:
```bash
cd /path/to/rick_clean_live
./util/obliterate_ghost_trading.sh
```

**Safety**:
- Does NOT modify ROLLBACK_SNAPSHOTS (backups are safe)
- Does NOT modify .git, .venv, or archived code
- All changes are version controlled and reversible
- No trading logic is modified, only labels and config flags

**Files Modified**:
- Python, shell, JSON, markdown, and config files in the active codebase
- Replaces ghost mode flags with canary/demo modes
- Updates progress file references

**Files Removed**:
- `ghost_charter_progress.json` (recreated as `canary_charter_progress.json` on next run)
- Any ghost-related log files in `logs/` directory

---

### live_plain_english.sh

**Purpose**: Monitor trading narration in human-readable format.

**What it does**:
- Tails `narration.jsonl` in real-time
- Parses JSON events and displays them in plain English
- Shows trade opens/closes, PnL, capital, and system events
- Does NOT affect the trading bot (read-only)

**Usage**:
```bash
cd /path/to/rick_clean_live
./util/live_plain_english.sh
```

**Example Output**:
```
RICK LIVE NARRATION — PLAIN ENGLISH
===================================
Ctrl+C stops THIS view only (bot keeps running)

RICK: BUY EUR_USD @ 1.0950  TP=1.0980  SL=1.0930
RICK: Closed EUR_USD — PnL $45.23
RICK: CANARY paper session running — capital $2,271.38, rules enforced.
RICK: Heartbeat — capital $2,316.61, cycle 42
```

**Stopping the Monitor**:
- Press `Ctrl+C` to stop the narration monitor
- The trading bot continues running in the background
- You can restart the monitor at any time

---

## System Modes

After running the obliteration script, only these modes are available:

### CANARY Mode
- **Purpose**: Real paper/practice trading with real API endpoints
- **Characteristics**:
  - Uses real market data
  - No real money at risk
  - Real API endpoints (OANDA practice, Coinbase sandbox)
  - Full Charter compliance enforcement
  - Trade IDs prefixed with `CANARY_CHARTER_`

### DEMO Mode
- **Purpose**: Sandbox/simulation for testing
- **Characteristics**:
  - Simulated market data
  - No API calls to brokers
  - Used for development and testing
  - No real or paper money involved

---

## Migration Notes

### What Changed
- All `GHOST_CHARTER` references → `CANARY_CHARTER`
- All `ghost_charter_progress.json` → `canary_charter_progress.json`
- Ghost/simulation flags removed from active codebase
- Mode toggles now limited to CANARY and DEMO

### What Stayed the Same
- Trading logic unchanged
- Charter compliance rules unchanged
- Risk management unchanged
- Broker connectors unchanged
- All backups and snapshots preserved

### Verification

After running the obliteration script, verify:

```bash
# Check no ghost references remain in active code
grep -r "GHOST_CHARTER" --include="*.py" --include="*.sh" | grep -v "ROLLBACK_SNAPSHOTS\|\.git\|\.venv"

# Should return empty (only archive references)

# Check narration file exists and is writable
ls -lh narration.jsonl

# Verify ROLLBACK_SNAPSHOTS untouched
git status | grep ROLLBACK_SNAPSHOTS
# Should return empty (no modifications)
```

---

## Troubleshooting

### "Permission denied" errors
Make sure scripts are executable:
```bash
chmod +x util/obliterate_ghost_trading.sh
chmod +x util/live_plain_english.sh
```

### narration.jsonl not found
The obliteration script creates this file automatically. If it's missing:
```bash
touch narration.jsonl
chmod 666 narration.jsonl
```

### jq command not found (for live_plain_english.sh)
Install jq:
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### Reversing Changes
All changes are version controlled. To revert:
```bash
git status
git restore <filename>  # Restore individual files
# or
git reset --hard HEAD~1  # Revert entire commit (use with caution)
```

---

## Related Documentation

- [CANARY_MODE_SETUP.md](../CANARY_MODE_SETUP.md) - Canary mode configuration
- [CANARY_NARRATION_INTEGRATION.md](../CANARY_NARRATION_INTEGRATION.md) - Narration system details
- [TWO_MODE_SYSTEM.md](../TWO_MODE_SYSTEM.md) - Two-mode system architecture

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the related documentation
3. Check git history: `git log --oneline util/`
4. Verify ROLLBACK_SNAPSHOTS are intact for safe rollback if needed
