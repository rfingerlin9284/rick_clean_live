# 🤖 RICK Narration Viewer - Quick Reference

## 🚀 Start Viewing Live Trading Activity
```bash
./view_live_narration.sh
```

Or from util directory:
```bash
cd util
./plain_english_narration.sh
```

## 📋 What You'll See

### Event Colors
- 🔍 **Cyan** - SCAN_START, SESSION_START/END
- 📊 **Yellow** - SIGNAL_GENERATED
- ❌ **Red** - SIGNAL_REJECTED, TRADE_CLOSED (loss), ERROR
- 🟢 **Green** - TRADE_OPENED, TRADE_CLOSED (win)
- 🐝 **Cyan** - HIVE_ANALYSIS
- 💹 **Magenta** - POSITION_UPDATE
- 🛡️ **Magenta** - RISK_CHECK

### Event Types Supported
1. SCAN_START - Market scanning initiated
2. SIGNAL_GENERATED - Trading signal detected
3. SIGNAL_REJECTED - Signal failed risk checks
4. TRADE_OPENED / ORDER_PLACED - New position
5. TRADE_CLOSED / ORDER_FILLED - Position closed
6. POSITION_UPDATE - P&L update
7. RISK_CHECK - Risk validation
8. HIVE_ANALYSIS - Multi-strategy consensus
9. SESSION_START - Trading session started
10. SESSION_END - Trading session ended
11. ERROR - System error

## 🎯 Usage Examples

### Basic Viewing
```bash
# Start viewer
./view_live_narration.sh

# Stop viewer
Press Ctrl+C
```

### View Raw Logs
```bash
# View raw JSON
tail -f narration.jsonl | jq .

# View specific event type
tail -f narration.jsonl | jq 'select(.event_type == "TRADE_OPENED")'

# Count events by type
jq -r '.event_type' narration.jsonl | sort | uniq -c
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `narration.jsonl` | Trading events log (JSON lines) |
| `util/plain_english_narration.sh` | Main viewer script |
| `view_live_narration.sh` | Launcher from project root |
| `AUTOMATED_TRADING_SETUP_GUIDE.md` | Full documentation |

## 🔧 Troubleshooting

### Narration Viewer Won't Start
```bash
# Check if jq is installed
which jq

# Install jq
sudo apt-get install jq
```

### No Events Showing
```bash
# Check if narration.jsonl exists and is being updated
ls -lh narration.jsonl
tail -1 narration.jsonl

# Check file permissions
ls -la util/plain_english_narration.sh
```

### Want to Filter Events
```bash
# Edit the script to filter specific events
# Look for the case statement around line 60
nano util/plain_english_narration.sh
```

## 🏦 Broker Configuration (Paper Trading Only)

| Broker | Account | Type | Risk |
|--------|---------|------|------|
| OANDA | 101-001-31210531-002 | Practice | $0 |
| Coinbase | Sandbox | Sandbox | $0 |
| IBKR | DUK880040 | Paper | $0 |

## 🔐 Safety Verified
✅ All configurations are PAPER TRADING only  
✅ No real money at risk  
✅ IBKR port 7497 (paper) NOT 7496 (live)  
✅ No ghost trading - real broker APIs  

## 📚 More Documentation
- **Setup Guide:** `AUTOMATED_TRADING_SETUP_GUIDE.md`
- **Paper Trading:** `PAPER_README.md`
- **General Reference:** `QUICK_REFERENCE.md`

## ⌨️ Keyboard Shortcuts
- `Ctrl+C` - Stop viewer
- `Ctrl+Z` - Pause viewer (then `fg` to resume)

## 💡 Pro Tips

### Run in Background with tmux
```bash
# Start tmux session
tmux new -s narration

# Start viewer
./view_live_narration.sh

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t narration
```

### Save Output to File
```bash
./view_live_narration.sh | tee narration_output.log
```

### Filter by Symbol
```bash
tail -f narration.jsonl | jq 'select(.symbol == "EUR_USD")'
```

---
**PIN: 841921** | **Last updated: 2025-11-20**
