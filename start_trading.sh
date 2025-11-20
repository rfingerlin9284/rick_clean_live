#!/bin/bash
# RICK Trading System - Unified Startup Script
# Automatically detects mode and starts appropriate trading engine

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================"
echo "🚀 RICK TRADING SYSTEM STARTUP"
echo "================================================================"
echo ""

# Check for environment file
if [ -f "master_paper_env.env" ]; then
    ENV_FILE="master_paper_env.env"
    MODE="PAPER/PRACTICE"
    echo "📝 Environment: PAPER TRADING MODE"
elif [ -f "master.env" ]; then
    ENV_FILE="master.env"
    MODE="AUTO-DETECT"
    echo "📝 Environment: AUTO-DETECT from master.env"
else
    echo "❌ Error: No environment file found!"
    echo "   Expected: master_paper_env.env or master.env"
    exit 1
fi

echo "   Using: $ENV_FILE"
echo ""

# Verify Python and dependencies
echo "🔍 Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "   ✓ $PYTHON_VERSION"

# Check critical dependencies
echo ""
echo "🔍 Verifying dependencies..."
python3 << 'PYEOF'
import sys
missing = []
for module in ['oandapyV20', 'pandas', 'numpy', 'websocket', 'dotenv']:
    try:
        __import__(module.replace('-', '_'))
    except ImportError:
        missing.append(module)

if missing:
    print(f"❌ Missing dependencies: {', '.join(missing)}")
    print("   Run: pip3 install -r requirements.txt")
    sys.exit(1)
else:
    print("   ✓ All critical dependencies installed")
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "================================================================"
echo "🎯 Starting Trading Engine..."
echo "================================================================"
echo ""

# Launch paper trading by default (safer)
if [ -f "launch_paper_trading.py" ]; then
    echo "▶ Launching: launch_paper_trading.py"
    echo ""
    python3 launch_paper_trading.py
elif [ -f "oanda_trading_engine.py" ]; then
    echo "▶ Launching: oanda_trading_engine.py"
    echo ""
    python3 oanda_trading_engine.py
elif [ -f "oanda_swing_paper_trading.py" ]; then
    echo "▶ Launching: oanda_swing_paper_trading.py"
    echo ""
    python3 oanda_swing_paper_trading.py
else
    echo "❌ Error: No trading engine found!"
    echo ""
    echo "Available alternatives:"
    echo "  • python3 launch_paper_trading.py"
    echo "  • python3 oanda_trading_engine.py"
    echo "  • bash start_paper.sh"
    exit 1
fi

echo ""
echo "================================================================"
echo "✅ Trading session ended"
echo "================================================================"
