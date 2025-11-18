# RICK Trading System - Troubleshooting Guide

## ✅ ISSUE RESOLVED: System Errors and Crashes

### Problem Summary
The system was experiencing crashes and errors due to missing Python dependencies and empty critical files.

### Root Causes Identified
1. **Missing Python Dependencies**: `websocket-client` and 12+ other packages were not installed
2. **Empty Critical Files**: `launch_paper_trading.py`, `start_trading.sh`, and others were empty
3. **Missing ML Modules**: `regime_detector.py` and `signal_analyzer.py` did not exist

### Solutions Implemented

#### 1. Dependencies Fixed ✅
All required Python packages have been installed:
- `websocket-client>=1.6.0` - Critical for OANDA connection
- `oandapyV20>=0.7.2` - OANDA API wrapper
- `pandas>=2.0.0` - Data analysis
- `numpy>=1.24.0` - Numerical computing
- `scikit-learn>=1.3.0` - Machine learning
- `streamlit>=1.28.0` - Dashboard
- And more...

**To verify installation:**
```bash
pip3 list | grep -E "(oandapyV20|websocket|pandas|numpy)"
```

#### 2. Critical Files Created ✅

**launch_paper_trading.py**
- Main launcher for paper trading
- Auto-loads environment variables
- Provides helpful error messages

**start_trading.sh**
- Unified startup script
- Checks dependencies before launching
- Auto-detects trading mode

**ml_learning/regime_detector.py**
- Market regime detection
- BULL/BEAR/SIDEWAYS classification

**ml_learning/signal_analyzer.py**
- Trading signal analysis
- RSI, MACD, SMA indicators

**view_tmux_session.sh**
- View active trading sessions
- Helpful tmux commands

---

## 🚀 How to Start the System

### Option 1: Quick Start (Recommended)
```bash
cd /home/runner/work/rick_clean_live/rick_clean_live
./start_trading.sh
```

### Option 2: Direct Python Launch
```bash
cd /home/runner/work/rick_clean_live/rick_clean_live
python3 launch_paper_trading.py
```

### Option 3: Specific Engine
```bash
# Paper trading
python3 oanda_swing_paper_trading.py

# OR
python3 oanda_trading_engine.py

# OR
bash start_paper_NOW.sh
```

---

## 🔍 Verification Steps

### 1. Check Dependencies
```bash
python3 << 'EOF'
modules = ['oandapyV20', 'pandas', 'numpy', 'websocket', 'dotenv', 'streamlit']
for m in modules:
    try:
        __import__(m.replace('-', '_'))
        print(f"✓ {m}")
    except ImportError:
        print(f"✗ {m} - MISSING")
EOF
```

### 2. Test Imports
```bash
python3 -c "from foundation.rick_charter import RickCharter; print('✓ Charter OK')"
python3 -c "from brokers.oanda_connector import OandaConnector; print('✓ OANDA OK')"
python3 -c "from ml_learning.regime_detector import RegimeDetector; print('✓ ML OK')"
```

### 3. Verify Environment Files
```bash
ls -lh master*.env
```
Expected files:
- `master.env` - Main environment configuration
- `master_paper_env.env` - Paper trading configuration

---

## ⚠️ Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'websocket'"
**Solution:**
```bash
pip3 install websocket-client
# OR install all dependencies:
pip3 install -r requirements.txt
```

### Issue: "ImportError: cannot import name 'RegimeDetector'"
**Solution:** Already fixed! The ML modules have been created.
```bash
# Verify:
python3 -c "from ml_learning.regime_detector import RegimeDetector; print('OK')"
```

### Issue: "launch_paper_trading.py is empty"
**Solution:** Already fixed! The file has been created with proper content.

### Issue: "Failed to resolve 'api-fxpractice.oanda.com'"
**Cause:** Network connectivity issue or DNS resolution problem
**Solution:**
1. Check internet connection
2. Verify OANDA API credentials in environment file
3. Try again - this is usually a temporary network issue

### Issue: "Charter PIN validation failed"
**Solution:** The system uses PIN 841921. This is already configured correctly.

---

## 📊 System Status Check

Run this command to check overall system health:
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("RICK Trading System - Health Check")
print("=" * 60)

# Check dependencies
print("\n1. Dependencies:")
deps = {
    'oandapyV20': 'OANDA API',
    'pandas': 'Data Analysis',
    'numpy': 'Numerical Computing',
    'websocket': 'WebSocket Client',
    'dotenv': 'Environment Loader',
}
for module, desc in deps.items():
    try:
        __import__(module.replace('-', '_'))
        print(f"   ✓ {desc}")
    except ImportError:
        print(f"   ✗ {desc} - MISSING")

# Check core modules
print("\n2. Core Modules:")
modules = {
    'foundation.rick_charter': 'Charter',
    'brokers.oanda_connector': 'OANDA Connector',
    'ml_learning.regime_detector': 'Regime Detector',
    'ml_learning.signal_analyzer': 'Signal Analyzer',
}
for module, desc in modules.items():
    try:
        __import__(module)
        print(f"   ✓ {desc}")
    except Exception as e:
        print(f"   ✗ {desc}: {e}")

# Check files
print("\n3. Critical Files:")
import os
files = [
    'launch_paper_trading.py',
    'oanda_trading_engine.py',
    'start_trading.sh',
    'requirements.txt',
    'master.env',
]
for f in files:
    if os.path.exists(f) and os.path.getsize(f) > 0:
        print(f"   ✓ {f}")
    elif os.path.exists(f):
        print(f"   ⚠ {f} (empty)")
    else:
        print(f"   ✗ {f} (missing)")

print("\n" + "=" * 60)
print("Health Check Complete")
print("=" * 60)
EOF
```

---

## 📝 Next Steps

1. **Verify System Health**: Run the health check above
2. **Start Paper Trading**: Use `./start_trading.sh` or `python3 launch_paper_trading.py`
3. **Monitor Logs**: Check `paper_trading_live.log` and `narration.jsonl`
4. **Dashboard**: Launch with `streamlit run dashboard.py` (if needed)

---

## 📞 Getting Help

If you encounter issues:

1. **Check logs**:
   ```bash
   tail -f paper_trading_live.log
   tail -f oanda_engine.log
   tail -f narration.jsonl
   ```

2. **Run health check** (command above)

3. **Verify environment**:
   ```bash
   grep TRADING_ENVIRONMENT master_paper_env.env
   ```

4. **Re-install dependencies** (if needed):
   ```bash
   pip3 install --force-reinstall -r requirements.txt
   ```

---

## ✅ Summary

**Status: SYSTEM READY FOR PAPER TRADING**

All critical issues have been resolved:
- ✅ All Python dependencies installed
- ✅ Missing files created and populated
- ✅ ML modules implemented
- ✅ Startup scripts functional
- ✅ Import errors fixed

You can now start paper trading with confidence!

```bash
# Start trading now:
./start_trading.sh
```
