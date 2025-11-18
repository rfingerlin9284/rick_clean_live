#!/usr/bin/env python3
"""
RICK Paper Trading Launcher
Simple launcher script for paper trading with OANDA practice account
PIN: 841921
"""

import sys
import os
from pathlib import Path

# Set up paths
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

# Load environment variables from master_paper_env.env
env_file = SCRIPT_DIR / 'master_paper_env.env'
if env_file.exists():
    print(f"📝 Loading paper trading environment from: {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
else:
    # Fallback to master.env
    env_file = SCRIPT_DIR / 'master.env'
    if env_file.exists():
        print(f"📝 Loading environment from: {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print("⚠️  Warning: No environment file found. Using default settings.")

# Import main trading engine
try:
    from oanda_trading_engine import OandaTradingEngine
    
    print("=" * 80)
    print("🚀 RICK PAPER TRADING SYSTEM")
    print("=" * 80)
    print("Environment: PRACTICE/PAPER")
    print("Mode: Safe Paper Trading (No Real Money)")
    print("=" * 80)
    print()
    
    # Launch the trading engine
    engine = OandaTradingEngine()
    engine.run()
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nTrying alternative launcher: oanda_swing_paper_trading.py")
    print()
    
    # Try to launch the swing trading engine instead
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("oanda_swing", str(SCRIPT_DIR / "oanda_swing_paper_trading.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e2:
        print(f"❌ Failed to launch alternative engine: {e2}")
        print("\nAvailable alternatives:")
        print("  1. python3 oanda_trading_engine.py")
        print("  2. python3 oanda_swing_paper_trading.py")
        print("  3. bash start_paper.sh")
        print("  4. bash start_paper_NOW.sh")
        sys.exit(1)

except KeyboardInterrupt:
    print("\n\n⏹️  Trading session interrupted by user")
    print("Shutting down safely...")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
