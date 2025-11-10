# 🎯 RICK SYSTEM - QUICK COMMAND REFERENCE

**For VSCode Agents & Developers**

---

## 📖 START HERE (Reading Order)

```bash
# 1. Executive Summary (start here)
cat README_ACTIVATION_PACKAGE.md

# 2. Complete Implementation Specifications
cat VSCODE_AGENT_MEGA_PROMPT_RICK_ACTIVATION.md

# 3. Status Tracking & Checklists
cat SYSTEM_STATUS_AND_ACTIVATION_GUIDE.md
```

---

## ✅ VERIFICATION COMMANDS

### Check System Status
```bash
# Run full verification (shows what exists vs what's needed)
bash scripts/verify_and_activate_all_systems.sh

# Expected output:
# - Lists all required components
# - Shows PASSED vs FAILED checks
# - Displays pass rate percentage
# - Exit codes: 0=ready, 1=partial, 2=failed
```

### Check Individual Components
```bash
# Check if Charter exists and has correct PIN
grep -n "PIN.*841921" foundation/rick_charter.py

# Check if Guardian Gates has validate_trade function
grep -n "def validate_trade" hive/guardian_gates.py

# Check if Regime Detector has all regimes
grep -n "BULLISH\|BEARISH\|SIDEWAYS\|CRASH" logic/regime_detector.py

# Check if Wolf Packs exist
ls -lh strategies/bullish_wolf.py strategies/bearish_wolf.py strategies/sideways_wolf.py

# Test Python imports
python3 -c "from foundation.rick_charter import RICKCharter; print('✅ Charter OK')"
python3 -c "from hive.guardian_gates import GuardianGates; print('✅ Gates OK')"
python3 -c "from strategies.bullish_wolf import BullishWolfPack; print('✅ Bullish Wolf OK')"
```

---

## 📥 IMPLEMENTATION COMMANDS

### 🚀 FASTEST: Use Import Script (5 minutes)

**If you already have the RICK files:**

```bash
# Quick import with default paths
bash scripts/import_existing_files.sh

# OR specify custom paths
bash scripts/import_existing_files.sh /path/to/RICK_LIVE_CLEAN /path/to/R_H_UNI

# Verify (should show 100%)
bash scripts/verify_and_activate_all_systems.sh
```

**What the import script does:**
- Creates all required directories
- Copies foundation, hive, logic, risk, brokers
- Copies trading engines (ghost, canary, capital_manager)
- Copies Wolf Pack strategies from R_H_UNI
- Shows summary of imported files

**Done in minutes!**

---

### Option A: Manual Copy from External Source (if script doesn't work)
```bash
# If files exist at /home/ing/RICK/ or custom location

# Copy foundation
mkdir -p foundation
cp -r /home/ing/RICK/RICK_LIVE_CLEAN/foundation/* ./foundation/

# Copy hive
mkdir -p hive
cp -r /home/ing/RICK/RICK_LIVE_CLEAN/hive/* ./hive/

# Copy logic
mkdir -p logic
cp -r /home/ing/RICK/RICK_LIVE_CLEAN/logic/* ./logic/

# Copy Wolf Packs
mkdir -p strategies
cp /home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py ./strategies/
cp /home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py ./strategies/
cp /home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py ./strategies/

# Copy trading engines
cp /home/ing/RICK/RICK_LIVE_CLEAN/ghost_trading_charter_compliant.py ./
cp /home/ing/RICK/RICK_LIVE_CLEAN/canary_trading_engine.py ./

# Copy risk management
mkdir -p risk
cp -r /home/ing/RICK/RICK_LIVE_CLEAN/risk/* ./risk/
cp /home/ing/RICK/RICK_LIVE_CLEAN/capital_manager.py ./

# Copy broker
mkdir -p brokers
cp /home/ing/RICK/RICK_LIVE_CLEAN/brokers/oanda_connector.py ./brokers/

# Verify everything
bash scripts/verify_and_activate_all_systems.sh
```

### Option B: Create Directory Structure for Manual Implementation
```bash
# Create all required directories
mkdir -p foundation hive logic strategies risk brokers

# Verify structure
tree -L 2 -d .

# Now implement each file following specs in:
# VSCODE_AGENT_MEGA_PROMPT_RICK_ACTIVATION.md
```

---

## 🚀 ACTIVATION COMMANDS

### Activate Paper Trading (Canary)
```bash
# Single 45-minute session
python3 canary_trading_engine.py --duration 45

# Continuous sessions (restarts every 45 minutes)
python3 canary_trading_engine.py --continuous --duration 45 --interval 60

# Run in background
nohup python3 canary_trading_engine.py --continuous --duration 45 > logs/canary.log 2>&1 &
```

### Activate Live Trading (CAUTION - Ghost Engine)
```bash
# ⚠️ USE WITH EXTREME CAUTION - LIVE TRADING ⚠️
python3 ghost_trading_charter_compliant.py

# Run with safety monitoring
python3 ghost_trading_charter_compliant.py --max-daily-loss 2 --max-position 2
```

### Monitor Active Systems
```bash
# Check if Canary is running
pgrep -f "canary_trading_engine.py"
ps aux | grep canary

# Check if Ghost is running
pgrep -f "ghost_trading"
ps aux | grep ghost

# View recent logs (if logging is implemented)
tail -f logs/canary.log
tail -f logs/trades.log
tail -f logs/gate_violations.log
```

---

## 🛑 EMERGENCY STOP COMMANDS

### Stop All Trading Immediately
```bash
# Kill all RICK trading processes
pkill -f "canary_trading_engine"
pkill -f "ghost_trading"

# Verify stopped
ps aux | grep -E "canary|ghost"

# Should show no results
```

### Review Logs After Stop
```bash
# Check what went wrong
tail -100 logs/gate_violations.log
tail -100 logs/trades.log
tail -100 logs/errors.log

# Check Charter compliance
grep "VIOLATION" logs/*.log
```

---

## 🧪 TESTING COMMANDS

### Test Individual Components
```bash
# Test Charter
python3 -c "
from foundation.rick_charter import RICKCharter
c = RICKCharter()
assert c.PIN == 841921
assert c.MAX_HOLD_HOURS == 6
assert c.MIN_RISK_REWARD == 3.2
print('✅ Charter tests passed')
"

# Test Guardian Gates
python3 -c "
from hive.guardian_gates import GuardianGates
g = GuardianGates()
# Add test trade params
test_trade = {
    'timeframe': 'M15',
    'notional': 20000,
    'risk_reward': 3.5,
    'hold_hours': 4
}
assert g.validate_trade(test_trade) == True
print('✅ Guardian Gates tests passed')
"

# Test Regime Detector
python3 -c "
from logic.regime_detector import RegimeDetector
r = RegimeDetector()
# Add test market data
test_data = {'trend': 1.5, 'volatility': 0.3}
regime = r.detect_regime(test_data)
assert regime in ['BULLISH', 'BEARISH', 'SIDEWAYS', 'CRASH']
print(f'✅ Regime detected: {regime}')
"

# Test Wolf Packs
python3 -c "
from strategies.bullish_wolf import BullishWolfPack
from strategies.bearish_wolf import BearishWolfPack
from strategies.sideways_wolf import SidewaysWolfPack
b = BullishWolfPack()
be = BearishWolfPack()
s = SidewaysWolfPack()
print('✅ All Wolf Packs loaded successfully')
"
```

### Run Canary Test Session
```bash
# Quick 5-minute test
python3 canary_trading_engine.py --duration 5 --regime-test

# Expected output should show:
# - Regime detection working
# - Strategy selection working
# - Gate validation working
# - Position sizing working
# - No Charter violations
```

---

## 📊 MONITORING COMMANDS

### System Health Check
```bash
# Create quick health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "🔍 RICK System Health Check"
echo "=========================="
echo ""

# Check processes
if pgrep -f "canary" > /dev/null; then
    echo "✅ Canary: RUNNING"
else
    echo "❌ Canary: STOPPED"
fi

# Check files
if [ -f "foundation/rick_charter.py" ]; then
    echo "✅ Charter: EXISTS"
else
    echo "❌ Charter: MISSING"
fi

# Check gate violations (if log exists)
if [ -f "logs/gate_violations.log" ]; then
    violations=$(wc -l < logs/gate_violations.log)
    echo "📊 Gate Violations: $violations"
else
    echo "ℹ️  No violation log found"
fi

echo ""
echo "Run full verification: bash scripts/verify_and_activate_all_systems.sh"
EOF

chmod +x health_check.sh
bash health_check.sh
```

### Watch Logs in Real-Time
```bash
# Create logs directory if needed
mkdir -p logs

# Watch multiple logs simultaneously
tail -f logs/canary.log logs/trades.log logs/gate_violations.log

# Or use multitail if available
multitail logs/canary.log logs/trades.log logs/gate_violations.log
```

---

## 🔧 MAINTENANCE COMMANDS

### Clean Up
```bash
# Remove temporary files
rm -rf __pycache__/ */__pycache__/
rm -f *.pyc */*.pyc

# Clean logs (backup first!)
mkdir -p logs/archive
mv logs/*.log logs/archive/
```

### Backup Configuration
```bash
# Backup entire system
tar -czf rick_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  foundation/ hive/ logic/ strategies/ risk/ brokers/ \
  *.py scripts/ --exclude='__pycache__' --exclude='*.pyc'

# List backups
ls -lh rick_backup_*.tar.gz
```

### Restore from Backup
```bash
# Extract backup
tar -xzf rick_backup_YYYYMMDD_HHMMSS.tar.gz

# Verify restoration
bash scripts/verify_and_activate_all_systems.sh
```

---

## 📚 DOCUMENTATION COMMANDS

### Generate Component List
```bash
# List all Python files by layer
echo "=== FOUNDATION ==="
ls -lh foundation/*.py

echo -e "\n=== HIVE ==="
ls -lh hive/*.py

echo -e "\n=== LOGIC ==="
ls -lh logic/*.py

echo -e "\n=== STRATEGIES ==="
ls -lh strategies/*.py

echo -e "\n=== RISK ==="
ls -lh risk/*.py

echo -e "\n=== BROKERS ==="
ls -lh brokers/*.py

echo -e "\n=== ENGINES ==="
ls -lh *_trading*.py
```

### Check Charter Compliance
```bash
# Verify Charter PIN in all files
grep -r "841921" . --include="*.py"

# Check for Charter imports
grep -r "from foundation.rick_charter import" . --include="*.py"

# Check for guardian gate calls
grep -r "guardian_gates\|GuardianGates" . --include="*.py"
```

---

## 🎯 ONE-LINER QUICK COMMANDS

```bash
# Quick verification
bash scripts/verify_and_activate_all_systems.sh

# Quick health check
ps aux | grep -E "canary|ghost" && echo "✅ Running" || echo "❌ Stopped"

# Quick stop all
pkill -f "canary\|ghost" && echo "✅ Stopped all trading"

# Quick start Canary
nohup python3 canary_trading_engine.py --continuous &

# Quick log check
tail -20 logs/canary.log logs/gate_violations.log

# Quick Charter check
grep "PIN.*841921" foundation/rick_charter.py && echo "✅ Charter OK"

# Quick import test
python3 -c "from foundation.rick_charter import RICKCharter" && echo "✅ Imports OK"
```

---

## 🆘 HELP COMMANDS

```bash
# Show this help
cat QUICK_COMMAND_REFERENCE.md

# Show mega prompt
cat VSCODE_AGENT_MEGA_PROMPT_RICK_ACTIVATION.md | less

# Show status guide
cat SYSTEM_STATUS_AND_ACTIVATION_GUIDE.md | less

# Show activation package
cat README_ACTIVATION_PACKAGE.md | less

# Show main README
cat README.md
```

---

**REMEMBER:**
- ✅ Always verify before activating: `bash scripts/verify_and_activate_all_systems.sh`
- ✅ Test with Canary before going live
- ✅ Monitor logs continuously
- ✅ Emergency stop: `pkill -f "canary\|ghost"`
- ✅ Charter compliance is NON-NEGOTIABLE

---

**END OF QUICK COMMAND REFERENCE**
