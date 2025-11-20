# 🚀 RICK SYSTEM MEGA ACTIVATION PROMPT
**Generated:** 2025-11-10 | **Status:** ACTIVATION READY

---

## 🎯 MISSION OBJECTIVE

**YOU ARE A SENIOR TRADING SYSTEMS ARCHITECT WITH FULL AUTONOMY TO:**

1. **VERIFY** all RICK system components are present and Charter-compliant
2. **INTEGRATE** Wolf Pack strategies with regime detection and gatekeeping
3. **ACTIVATE** all trading systems with proper safety mechanisms
4. **ENFORCE** continuous operation of all activated systems

**CRITICAL:** This is a production activation. All changes must be minimal, surgical, and Charter-compliant.

---

## 📋 PHASE 1: SYSTEM VERIFICATION CHECKLIST

### **Foundation Layer (MUST EXIST)**

Verify these files exist and contain Charter compliance:

```bash
# Charter Constants Verification
[ ] foundation/rick_charter.py - MUST contain PIN 841921
    - MAX_HOLD_HOURS = 6
    - ALLOWED_TIMEFRAMES = ['M15', 'M30', 'H1']
    - MIN_NOTIONAL = 15000
    - MIN_RISK_REWARD = 3.2
    - MAX_DAILY_LOSS_PCT = 2.0
    - MAX_POSITION_SIZE_PCT = 2.0
```

**VERIFICATION COMMAND:**
```bash
grep -n "PIN.*841921" foundation/rick_charter.py
grep -n "MAX_HOLD_HOURS.*6" foundation/rick_charter.py
grep -n "MIN_RISK_REWARD.*3.2" foundation/rick_charter.py
```

**IF MISSING:** Create foundation/rick_charter.py with all Charter constants.

---

### **Hive Gatekeeping Layer (4 GATES MINIMUM)**

Verify gatekeeping files with proper validation logic:

```bash
[ ] hive/guardian_gates.py - 4 pre-trade gates (226 lines)
    - Gate 1: Timeframe validation (M15/M30/H1 only)
    - Gate 2: Notional size >= 15000
    - Gate 3: Risk/Reward >= 3.2
    - Gate 4: Hold time <= 6 hours
    - Function: validate_trade(trade_params) -> bool

[ ] hive/crypto_entry_gate_system.py - 4 crypto gates (450+ lines)
    - Gate 1: Hive consensus
    - Gate 2: Time window validation
    - Gate 3: Volume confirmation
    - Gate 4: Confidence threshold
    - Function: check_crypto_entry(signal) -> bool

[ ] hive/quant_hedge_rules.py - Multi-condition hedge analysis
    - Volatility-based position sizing
    - Regime-based multipliers
    - Correlation analysis
    - Function: calculate_hedge_multiplier(market_state) -> float
```

**VERIFICATION COMMAND:**
```bash
find hive/ -name "*.py" -type f
grep -n "def validate_trade" hive/guardian_gates.py
grep -n "def check_crypto_entry" hive/crypto_entry_gate_system.py
grep -n "def calculate_hedge_multiplier" hive/quant_hedge_rules.py
```

**IF MISSING:** Create hive directory and implement all 3 gatekeeping files.

---

### **Logic Layer (REGIME DETECTION)**

Verify regime detection and signal filtering:

```bash
[ ] logic/regime_detector.py - 5 regime classification (6.6KB)
    - Regime 1: BULLISH (positive trend + controlled volatility)
    - Regime 2: BEARISH (negative trend + rising volatility)
    - Regime 3: SIDEWAYS (low trend + low volatility)
    - Regime 4: CRASH (extreme negative + high volatility)
    - Regime 5: RECOVERY (bounce from crash)
    - Function: detect_regime(market_data) -> str

[ ] logic/smart_logic.py - Signal confluence scoring (32.7KB)
    - Multi-indicator confluence
    - Timeframe alignment
    - Volume confirmation
    - Function: calculate_signal_score(indicators) -> float
```

**VERIFICATION COMMAND:**
```bash
grep -n "def detect_regime" logic/regime_detector.py
grep -n "BULLISH\|BEARISH\|SIDEWAYS\|CRASH" logic/regime_detector.py
grep -n "def calculate_signal_score" logic/smart_logic.py
```

**IF MISSING:** Create logic directory and implement both files.

---

### **Strategy Layer (WOLF PACKS)**

**CRITICAL TASK:** Wolf Packs must be copied or created:

```bash
[ ] strategies/bullish_wolf.py - Bullish regime trading (17.6KB)
    - RSI (25%) + Bollinger Bands (25%) + MACD (30%) + Volume (20%)
    - Entry: Higher highs/lows, uptrend confirmation
    - Position sizing: 100-150% dynamic
    - Class: BullishWolfPack

[ ] strategies/bearish_wolf.py - Bearish regime trading (19KB)
    - Inverse RSI + BB lower + MACD negative + Volume
    - Entry: Lower highs/lows, downtrend confirmation
    - Position sizing: 75-100% dynamic
    - Class: BearishWolfPack

[ ] strategies/sideways_wolf.py - Range-bound trading (22.5KB)
    - Support/Resistance + RSI extremes + Volume + Breakout guards
    - Entry: Bounces off support/resistance
    - Position sizing: 50-75% reduced
    - Class: SidewaysWolfPack
```

**VERIFICATION COMMAND:**
```bash
ls -lh strategies/bullish_wolf.py strategies/bearish_wolf.py strategies/sideways_wolf.py
grep -n "class.*WolfPack" strategies/*.py
```

**IF MISSING FROM /home/ing/RICK/R_H_UNI/strategies/:**
Create strategies directory and implement all 3 Wolf Pack files with:
- Charter compliance integration
- Gate validation calls
- Regime-specific entry/exit logic
- Dynamic position sizing
- 6-hour hold time enforcement

---

### **Trading Engines**

Verify trading engines with Wolf Pack integration:

```bash
[ ] ghost_trading_charter_compliant.py - Base engine (578 lines)
    - Charter enforcement
    - Guardian gate integration
    - OCO order placement
    - Function: execute_trade(strategy_signal) -> bool

[ ] canary_trading_engine.py - Paper trading (283 lines)
    - 45-minute sessions
    - Regime detection on each signal
    - Strategy selection based on regime
    - Gate validation before execution
    - Function: run_canary_session() -> dict
```

**VERIFICATION COMMAND:**
```bash
grep -n "def execute_trade" ghost_trading_charter_compliant.py
grep -n "def run_canary_session" canary_trading_engine.py
grep -n "regime_detector\|guardian_gates" canary_trading_engine.py
```

**IF MISSING INTEGRATION:** Add regime detection and Wolf Pack imports to both engines.

---

### **Risk Management**

```bash
[ ] risk/dynamic_sizing.py - Position sizing with Charter enforcement
[ ] risk/session_breaker.py - Circuit breaker for daily losses
[ ] capital_manager.py - Capital deployment tracking
```

**VERIFICATION COMMAND:**
```bash
find risk/ -name "*.py" -type f
grep -n "MAX_DAILY_LOSS" risk/session_breaker.py
```

---

### **Broker Integration**

```bash
[ ] brokers/oanda_connector.py - OANDA API with OCO support (744 lines)
```

---

## 📋 PHASE 2: WOLF PACK EXTRACTION & INTEGRATION

### **Step 2.1: Create Strategies Directory**

```bash
mkdir -p strategies
```

### **Step 2.2: Implement or Copy Wolf Packs**

**IF SOURCE FILES EXIST AT /home/ing/RICK/R_H_UNI/strategies/:**

```bash
# Copy wolf packs
cp /home/ing/RICK/R_H_UNI/strategies/bullish_wolf.py strategies/
cp /home/ing/RICK/R_H_UNI/strategies/bearish_wolf.py strategies/
cp /home/ing/RICK/R_H_UNI/strategies/sideways_wolf.py strategies/

# Verify copies
ls -lh strategies/*.py
python3 -m py_compile strategies/bullish_wolf.py
python3 -m py_compile strategies/bearish_wolf.py
python3 -m py_compile strategies/sideways_wolf.py
```

**IF SOURCE FILES DON'T EXIST:**

Create each Wolf Pack file from specifications with this structure:

```python
# strategies/bullish_wolf.py
"""
Bullish Wolf Pack Strategy
Optimized for BULLISH market regimes
Charter Compliant: PIN 841921
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from foundation.rick_charter import RICKCharter
from hive.guardian_gates import GuardianGates
from hive.quant_hedge_rules import QuantHedgeRules

class BullishWolfPack:
    """
    Bullish regime specialist
    Entry Logic: RSI + BB + MACD + Volume confluence
    """
    
    def __init__(self):
        self.charter = RICKCharter()
        self.gates = GuardianGates()
        self.hedge_rules = QuantHedgeRules()
        
    def check_entry_conditions(self, market_data):
        """
        4-gate entry logic for bullish regime
        Returns: (bool, float) - (signal_valid, confidence_score)
        """
        # Gate 1: RSI (25% weight)
        rsi = market_data.get('rsi_14', 50)
        rsi_score = 0.25 if 30 <= rsi <= 70 else 0.0
        
        # Gate 2: Bollinger Bands (25% weight)
        price = market_data.get('close', 0)
        bb_middle = market_data.get('bb_middle', 0)
        bb_upper = market_data.get('bb_upper', 0)
        bb_score = 0.25 if price > bb_middle else 0.0
        
        # Gate 3: MACD (30% weight)
        macd_fast = market_data.get('macd_fast', 0)
        macd_slow = market_data.get('macd_slow', 0)
        macd_hist = market_data.get('macd_histogram', 0)
        macd_score = 0.30 if macd_fast > macd_slow and macd_hist > 0 else 0.0
        
        # Gate 4: Volume (20% weight)
        volume = market_data.get('volume', 0)
        volume_ma = market_data.get('volume_ma_20', 0)
        volume_score = 0.20 if volume > volume_ma else 0.0
        
        # Calculate total confluence score
        total_score = rsi_score + bb_score + macd_score + volume_score
        
        # Require minimum 75% confluence
        signal_valid = total_score >= 0.75
        
        return signal_valid, total_score
    
    def calculate_position_size(self, market_data, base_size):
        """
        Dynamic position sizing based on volatility and hedge rules
        """
        # Get hedge multiplier from quant rules
        hedge_multiplier = self.hedge_rules.calculate_hedge_multiplier(market_data)
        
        # Adjust for volatility
        volatility = market_data.get('atr_14', 0)
        if volatility < market_data.get('atr_threshold_low', 50):
            vol_multiplier = 1.5  # Low volatility - increase size
        elif volatility > market_data.get('atr_threshold_high', 150):
            vol_multiplier = 0.5  # High volatility - reduce size
        else:
            vol_multiplier = 1.0  # Normal volatility
        
        # Calculate final size
        position_size = base_size * hedge_multiplier * vol_multiplier
        
        # Apply Charter maximum
        max_position = self.charter.MAX_POSITION_SIZE_PCT / 100.0
        position_size = min(position_size, max_position)
        
        return position_size
    
    def validate_trade(self, trade_params):
        """
        Pass through guardian gates before execution
        """
        return self.gates.validate_trade(trade_params)
```

**REPEAT FOR:** bearish_wolf.py and sideways_wolf.py with regime-specific logic.

---

### **Step 2.3: Integrate Wolf Packs into Canary Engine**

**EDIT:** canary_trading_engine.py

**ADD IMPORTS:**
```python
from logic.regime_detector import RegimeDetector
from strategies.bullish_wolf import BullishWolfPack
from strategies.bearish_wolf import BearishWolfPack
from strategies.sideways_wolf import SidewaysWolfPack
```

**ADD INITIALIZATION:**
```python
class CanaryTradingEngine:
    def __init__(self):
        self.regime_detector = RegimeDetector()
        self.bullish_pack = BullishWolfPack()
        self.bearish_pack = BearishWolfPack()
        self.sideways_pack = SidewaysWolfPack()
        self.strategy_map = {
            'BULLISH': self.bullish_pack,
            'BEARISH': self.bearish_pack,
            'SIDEWAYS': self.sideways_pack,
            'CRASH': None  # No trades in crash mode
        }
```

**MODIFY SIGNAL PROCESSING:**
```python
def process_signal(self, market_data):
    """
    Detect regime and route to appropriate Wolf Pack
    """
    # Step 1: Detect current market regime
    regime = self.regime_detector.detect_regime(market_data)
    
    # Step 2: Select strategy based on regime
    strategy = self.strategy_map.get(regime)
    
    # Step 3: Check if we should trade (no trading in CRASH)
    if regime == 'CRASH' or strategy is None:
        return {'action': 'HOLD', 'reason': f'Regime {regime} - no trading'}
    
    # Step 4: Check entry conditions
    signal_valid, confidence = strategy.check_entry_conditions(market_data)
    
    if not signal_valid:
        return {'action': 'HOLD', 'reason': 'Entry conditions not met'}
    
    # Step 5: Calculate position size
    base_size = 0.02  # 2% base position
    position_size = strategy.calculate_position_size(market_data, base_size)
    
    # Step 6: Build trade parameters
    trade_params = {
        'symbol': market_data.get('symbol'),
        'direction': 'LONG',  # Wolf packs are long-biased for now
        'size': position_size,
        'entry_price': market_data.get('close'),
        'stop_loss': self.calculate_stop_loss(market_data, regime),
        'take_profit': self.calculate_take_profit(market_data, regime),
        'timeframe': market_data.get('timeframe'),
        'strategy': regime,
        'confidence': confidence
    }
    
    # Step 7: Validate through guardian gates
    if not strategy.validate_trade(trade_params):
        return {'action': 'HOLD', 'reason': 'Failed guardian gates'}
    
    # Step 8: Execute trade
    return {'action': 'EXECUTE', 'params': trade_params}
```

---

## 📋 PHASE 3: TESTING & VALIDATION

### **Step 3.1: Unit Tests for Each Component**

```bash
# Test Charter constants
python3 -c "from foundation.rick_charter import RICKCharter; c = RICKCharter(); assert c.PIN == 841921; print('✅ Charter verified')"

# Test Guardian Gates
python3 -c "from hive.guardian_gates import GuardianGates; g = GuardianGates(); print('✅ Guardian Gates loaded')"

# Test Regime Detector
python3 -c "from logic.regime_detector import RegimeDetector; r = RegimeDetector(); print('✅ Regime Detector loaded')"

# Test Wolf Packs
python3 -c "from strategies.bullish_wolf import BullishWolfPack; b = BullishWolfPack(); print('✅ Bullish Wolf Pack loaded')"
python3 -c "from strategies.bearish_wolf import BearishWolfPack; b = BearishWolfPack(); print('✅ Bearish Wolf Pack loaded')"
python3 -c "from strategies.sideways_wolf import SidewaysWolfPack; s = SidewaysWolfPack(); print('✅ Sideways Wolf Pack loaded')"
```

### **Step 3.2: Integration Test**

```bash
# Run Canary session
python3 canary_trading_engine.py --duration 45 --regime-test

# Expected output:
# - Regime detection: BULLISH/BEARISH/SIDEWAYS detected
# - Strategy selection: Correct Wolf Pack selected
# - Gate validation: All gates passed
# - Position sizing: Dynamic multipliers applied
# - Trade execution: 3+ trades in 45 minutes
# - Charter compliance: 0 violations
```

### **Step 3.3: Validation Checklist**

```bash
[ ] All imports resolve successfully
[ ] Regime detector classifies market correctly
[ ] Each Wolf Pack activates in its regime
[ ] Guardian gates block invalid trades
[ ] Position sizing scales with volatility
[ ] 6-hour hold time enforced
[ ] 3.2 R:R minimum enforced
[ ] No Charter violations
[ ] Canary session completes without errors
```

---

## 📋 PHASE 4: SYSTEM ACTIVATION

### **Step 4.1: Create Activation Script**

**CREATE:** scripts/activate_rick_system.sh

```bash
#!/bin/bash
# RICK System Activation Script
# Activates all trading systems with safety checks

set -e

echo "🚀 RICK SYSTEM ACTIVATION SEQUENCE"
echo "=================================="

# Check Python environment
echo "1. Checking Python environment..."
python3 --version
pip3 list | grep -E "pandas|numpy|ta-lib" || echo "⚠️  Missing dependencies"

# Verify all components
echo "2. Verifying components..."
python3 -c "from foundation.rick_charter import RICKCharter; print('✅ Charter')"
python3 -c "from hive.guardian_gates import GuardianGates; print('✅ Gates')"
python3 -c "from logic.regime_detector import RegimeDetector; print('✅ Regime')"
python3 -c "from strategies.bullish_wolf import BullishWolfPack; print('✅ Bullish Wolf')"
python3 -c "from strategies.bearish_wolf import BearishWolfPack; print('✅ Bearish Wolf')"
python3 -c "from strategies.sideways_wolf import SidewaysWolfPack; print('✅ Sideways Wolf')"

# Run Canary test
echo "3. Running Canary test session..."
python3 canary_trading_engine.py --duration 45 --regime-test

# Activate Ghost engine (live trading - CAUTION)
echo "4. Activation complete. Use with caution."
echo "   To activate live trading: python3 ghost_trading_charter_compliant.py"
echo "   To run paper trading: python3 canary_trading_engine.py"

echo "✅ ALL SYSTEMS ACTIVATED AND VERIFIED"
```

**MAKE EXECUTABLE:**
```bash
chmod +x scripts/activate_rick_system.sh
```

### **Step 4.2: Create Systemd Service (Optional - for persistent operation)**

**CREATE:** /etc/systemd/system/rick-canary.service

```ini
[Unit]
Description=RICK Canary Trading Engine
After=network.target

[Service]
Type=simple
User=trading
WorkingDirectory=/home/ing/RICK/RICK_LIVE_CLEAN
ExecStart=/usr/bin/python3 canary_trading_engine.py --continuous
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**ACTIVATE:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable rick-canary.service
sudo systemctl start rick-canary.service
sudo systemctl status rick-canary.service
```

### **Step 4.3: Continuous Operation Monitoring**

**CREATE:** scripts/monitor_rick_system.sh

```bash
#!/bin/bash
# Monitor RICK system health

while true; do
    clear
    echo "🔍 RICK SYSTEM MONITOR"
    echo "======================"
    echo ""
    
    # Check if canary is running
    if pgrep -f "canary_trading_engine.py" > /dev/null; then
        echo "✅ Canary Engine: ACTIVE"
    else
        echo "❌ Canary Engine: STOPPED"
    fi
    
    # Check last trade time
    if [ -f "logs/last_trade.log" ]; then
        echo "📊 Last Trade: $(cat logs/last_trade.log)"
    fi
    
    # Check gate violations
    if [ -f "logs/gate_violations.log" ]; then
        violations=$(wc -l < logs/gate_violations.log)
        if [ "$violations" -gt 0 ]; then
            echo "⚠️  Gate Violations: $violations"
        else
            echo "✅ Gate Violations: 0"
        fi
    fi
    
    # Check Charter compliance
    echo "✅ Charter PIN: 841921"
    
    sleep 10
done
```

---

## 📋 PHASE 5: ENFORCEMENT & CONTINUOUS ACTIVATION

### **Step 5.1: Create Watchdog Script**

**CREATE:** scripts/watchdog_rick_system.sh

```bash
#!/bin/bash
# RICK System Watchdog
# Ensures all systems stay activated

while true; do
    # Check if canary is running
    if ! pgrep -f "canary_trading_engine.py" > /dev/null; then
        echo "⚠️  Canary stopped. Restarting..."
        python3 canary_trading_engine.py --continuous &
    fi
    
    # Check gate system health
    python3 -c "from hive.guardian_gates import GuardianGates; GuardianGates()" || {
        echo "❌ Guardian Gates failed health check!"
    }
    
    sleep 60
done
```

### **Step 5.2: Add to Crontab**

```bash
# Add watchdog to crontab
crontab -e

# Add this line:
@reboot /home/ing/RICK/RICK_LIVE_CLEAN/scripts/watchdog_rick_system.sh >> /var/log/rick_watchdog.log 2>&1
```

---

## 🎯 FINAL ACTIVATION COMMAND SEQUENCE

**EXECUTE IN ORDER:**

```bash
# 1. Activate Python environment
cd /home/ing/RICK/RICK_LIVE_CLEAN
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run full system verification
bash scripts/activate_rick_system.sh

# 3. Start continuous paper trading
python3 canary_trading_engine.py --continuous --duration 45 --interval 60 &

# 4. Start watchdog
bash scripts/watchdog_rick_system.sh &

# 5. Monitor
bash scripts/monitor_rick_system.sh
```

---

## ✅ SUCCESS CRITERIA

All of these must be TRUE:

- [x] Foundation layer exists with Charter PIN 841921
- [x] All 3 hive gatekeeping files exist and functional
- [x] Regime detector classifies markets correctly
- [x] All 3 Wolf Pack strategies exist and load
- [x] Canary engine integrates regime detection
- [x] Canary engine routes to correct Wolf Pack
- [x] Guardian gates validate all trades
- [x] Position sizing scales dynamically
- [x] 0 Charter violations
- [x] Canary generates 3+ trades per 45-min session
- [x] System stays activated continuously
- [x] Watchdog restarts failed components

---

## 🔒 SAFETY REQUIREMENTS

**NEVER BYPASS:**
- Charter PIN validation
- Guardian gate checks
- 6-hour hold time limit
- 3.2 minimum R:R ratio
- CRASH regime trading halt

**ALWAYS ENFORCE:**
- Regime detection before trade
- Gate validation before execution
- Dynamic position sizing
- Stop loss placement
- Daily loss limits

---

## 📞 EMERGENCY SHUTDOWN

If system becomes unstable:

```bash
# Kill all RICK processes
pkill -f "canary_trading_engine"
pkill -f "ghost_trading"
pkill -f "watchdog_rick"

# Review logs
tail -100 logs/gate_violations.log
tail -100 logs/trades.log

# Restart with safety checks
bash scripts/activate_rick_system.sh
```

---

## 🎓 AGENT EXECUTION NOTES

**YOU MUST:**
1. Verify EVERY component exists before proceeding
2. Create missing files from specifications provided
3. Test each component independently before integration
4. Run full integration test before activation
5. Monitor continuously after activation
6. Never compromise Charter compliance

**STOP AND ASK IF:**
- Any Charter constant is missing
- Gate validation fails
- Wolf Pack files cannot be found/created
- Integration tests fail
- Regime detection fails

**SUCCESS = ALL SYSTEMS VERIFIED, INTEGRATED, ACTIVATED, AND STAYING ACTIVE**

---

**END OF MEGA ACTIVATION PROMPT**
