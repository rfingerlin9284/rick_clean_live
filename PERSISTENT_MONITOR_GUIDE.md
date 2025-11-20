# 🤖 RICK Autonomous System - Persistent Monitoring Guide

## Overview

The RICK Persistent Monitor provides a comprehensive, self-refreshing view of all 100+ advanced features and system health in a persistent terminal window.

## Quick Start

### From VSCode Command Palette

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Tasks: Run Task"
3. Select **"RICK: 📺 Persistent Monitor (All Features)"**

This will open a dedicated terminal that shows:
- All 100+ feature status (✅/❌)
- RICK Hive Mind → RBOTzilla integration status
- Live trading narration feed (last 10 events)
- Autonomous system health
- Auto-refreshes every 30 seconds

### From Command Line

```bash
# Start the persistent monitor
./rick_persistent_monitor.sh start

# Stop the monitor
./rick_persistent_monitor.sh stop

# Check monitor status
./rick_persistent_monitor.sh status
```

## Features Monitored (100+ Total)

### 📊 SECTION 1: Core Trading Engine (20 features)
- OANDA Connector
- Multi-Broker Engine
- Signal Generation
- Position Management
- Guardian Gates
- Risk Management
- OCO Order System
- Charter Compliance
- Paper Trading Mode
- Live Trading Engine
- OANDA Trading Engine
- Canary Trading System
- Position Police
- Trailing Stop Logic
- Market Data Fetcher
- Notional Validator
- TP-PnL Floor Gate
- Trade Lifecycle Manager
- Enhanced RICK Engine
- Integrated Wolf Engine

### 🧠 SECTION 2: Hive Mind & AI Systems (15 features)
- RICK Hive Mind
- Hive Browser Connector
- Browser AI Connector
- Hive Mind Processor
- Adaptive RICK
- RICK Local AI
- Quant Hedge Rules
- Crypto Entry Gate
- Strategy Aggregator
- Correlation Monitor
- Wolf Pack System
- RBOTzilla Golden Age
- RBOTzilla Enhanced
- ML Intelligence
- Swarm Intelligence

### 📈 SECTION 3: Analysis & Optimization (15 features)
- Trading Optimizer
- Performance Analytics
- Parameter Manager
- Market Hours Manager
- Timezone Manager
- USD Converter
- Progress Tracker
- System Mapper
- Dual Connector
- Stochastic Engine
- Sentiment Analysis
- Market Data Diagnostic
- Breakpoint Audit
- Quant Hedge Engine
- Capital Manager

### 🛡️ SECTION 4: Risk & Governance (12 features)
- Risk Manager
- Position Limits
- Drawdown Monitor
- Charter Immutability
- Governance Lock
- Runtime Guard
- Sentinel Mode
- Integrity Checker
- Position Guardian
- Mode Manager
- Live Safety Verification
- Paper Mode Validation

### 📡 SECTION 5: Monitoring & Alerts (10 features)
- Live Monitor
- Narration System
- Narration Logger
- Process Narrator
- Alert Notifier
- Terminal Display
- RICK Live Monitor
- Dashboard System
- Dashboard Supervisor
- Status Reporter

### 🔧 SECTION 6: Utilities & Infrastructure (13 features)
- RICK Logging
- Retry Logic
- Progress Manager
- Load Environment
- Verify Brokers
- Verify System
- Verify Endpoints
- Show Endpoint Status
- Test Integration
- Unified System Test
- RBOTzilla Client
- Live Preflight Check
- System Diagnostic

### 🚀 SECTION 7: Deployment & Launch (10 features)
- Start Full System
- Start Paper Trading
- Start with Integrity
- Launch Advanced Dashboard
- Launch Complete Dashboard
- Launch OANDA Focus
- Launch Canary
- Monitor Tmux
- Monitor Paper Trading
- Monitor Narration

## Monitor Display

The monitor shows:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║              🤖 RICK AUTONOMOUS TRADING SYSTEM - FEATURE STATUS              ║
║                    HIVE MIND → RBOTZILLA INTEGRATION                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

System Timestamp: 2025-11-20 08:50:07 UTC
PIN Authentication: 841921

[Feature sections with ✅/❌ status indicators]

════════════════════════════════════════════════════════════════════════════════
📊 FEATURE SUMMARY
════════════════════════════════════════════════════════════════════════════════
Active Features: 73 / 95
System Health: 76%
Status: GOOD - Most systems operational

════════════════════════════════════════════════════════════════════════════════
🔗 AUTONOMOUS SYSTEM STATUS
════════════════════════════════════════════════════════════════════════════════
✅ Trading Engine: ONLINE
✅ Narration System: ACTIVE (19M)
⚠️  Dashboard: OFFLINE
✅ RICK Hive Mind: READY
✅ RBOTzilla System: READY

════════════════════════════════════════════════════════════════════════════════
📡 LIVE TRADING NARRATION (last 10 events)
════════════════════════════════════════════════════════════════════════════════
[Color-coded live events from narration.jsonl]

🔄 Auto-refresh in 30 seconds...
```

## Persistence Behavior

### Auto-Refresh
- Refreshes every 30 seconds automatically
- Shows real-time feature status
- Updates narration feed continuously

### Self-Healing
- While the monitor is running (flag file exists), it will continuously refresh
- If you close the terminal in VSCode, you can restart it by running the task again
- The monitor maintains its state via the `/tmp/rick_monitor_active` flag file

### Manual Control
```bash
# Check if monitor is running
./rick_persistent_monitor.sh status

# Stop the monitor (removes flag file and stops process)
./rick_persistent_monitor.sh stop

# Restart if needed
./rick_persistent_monitor.sh start
```

## VSCode Integration

### Tasks Available
1. **RICK: 📺 Persistent Monitor (All Features)** - Start monitoring
2. **RICK: ⏹️ Stop Persistent Monitor** - Stop monitoring
3. **RICK: 📊 Monitor Status** - Check if running

### Opening in VSCode
The monitor is designed to run in a VSCode terminal panel. When you run the task:
1. A new dedicated terminal panel opens
2. The monitor displays and starts auto-refreshing
3. Terminal stays open even if you click away
4. Re-running the task will show current status or restart if stopped

## Feature Status Indicators

| Indicator | Meaning |
|-----------|---------|
| ✅ | Feature is active and available |
| ❌ | Feature file not found or not configured |

## System Health Levels

| Percentage | Status | Description |
|------------|--------|-------------|
| 90-100% | EXCELLENT | All critical systems online |
| 75-89% | GOOD | Most systems operational |
| 50-74% | DEGRADED | Some systems offline |
| <50% | CRITICAL | Many systems offline |

## Troubleshooting

### Monitor Won't Start
```bash
# Check if already running
./rick_persistent_monitor.sh status

# If stale, clean up
rm -f /tmp/rick_monitor_active /tmp/rick_monitor.pid

# Try again
./rick_persistent_monitor.sh start
```

### Terminal Closes Immediately
- This is normal if monitor was already stopped
- Check status first: `./rick_persistent_monitor.sh status`
- Start if needed: `./rick_persistent_monitor.sh start`

### Want to Run in Background
The monitor is designed to run in foreground for VSCode integration. For background use:
```bash
nohup ./rick_persistent_monitor.sh start > /tmp/rick_monitor.log 2>&1 &
```

## Comparison with Other Monitoring Tools

| Tool | Purpose | Auto-Refresh | Feature Count | VSCode Integrated |
|------|---------|--------------|---------------|-------------------|
| `rick_persistent_monitor.sh` | All features + system health | ✅ 30s | 100+ | ✅ |
| `view_live_narration.sh` | Narration only | ✅ Real-time | N/A | ⚠️ Manual |
| `start_monitor_tmux.sh` | Multi-pane tmux | ⚠️ Manual | Limited | ❌ |
| `live_monitor.py` | Python monitoring | ✅ 60s | Metrics only | ⚠️ Manual |

## Pro Tips

### Run on Startup
Add to your startup script or VSCode workspace settings to auto-launch:
```json
{
  "tasks": {
    "runOn": "folderOpen",
    "tasks": ["RICK: 📺 Persistent Monitor (All Features)"]
  }
}
```

### Multiple Monitors
You can run multiple monitoring views simultaneously:
- Persistent Monitor (all features)
- Live Narration (`./view_live_narration.sh`)
- TMUX Multi-pane (`./start_monitor_tmux.sh`)

### Customize Refresh Rate
Edit line 651 in `rick_persistent_monitor.sh`:
```bash
sleep 30  # Change to desired seconds
```

## Related Documentation

- `AUTOMATED_TRADING_SETUP_GUIDE.md` - Complete trading setup
- `NARRATION_VIEWER_QUICK_REF.md` - Narration viewer guide
- `ADVANCED_FEATURES_COMPLETE_AUDIT.md` - Full feature documentation
- `MONITORING_QUICK_REFERENCE.md` - General monitoring guide

---

**PIN: 841921** | **Last Updated: 2025-11-20**
