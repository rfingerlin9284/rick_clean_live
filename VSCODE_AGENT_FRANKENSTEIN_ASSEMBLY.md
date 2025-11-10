# 🔧 VSCODE AGENT: ASSEMBLE RICK FROM EXISTING CODE

**Mission:** Use VSCode agent to combine existing RICK code from multiple local and GitHub repos into this repository.

**Key Constraint:** NO TA-LIB - Pure Python only, use bash commands where needed.

---

## 🎯 AGENT INSTRUCTIONS

### Phase 1: Locate All Source Code

**VSCode Agent Prompt:**
```
Search my local filesystem and GitHub repos for RICK trading system files:

LOCAL SEARCH PATHS:
- /home/ing/RICK/RICK_LIVE_CLEAN/
- /home/ing/RICK/R_H_UNI/
- ~/Desktop/RICK/
- ~/Documents/trading/
- ~/Downloads/

GITHUB REPOS TO CHECK:
- Search my GitHub account for repos containing:
  - "rick" OR "trading" OR "wolf" OR "charter"
  - Files: rick_charter.py, guardian_gates.py, regime_detector.py
  - Files: bullish_wolf.py, bearish_wolf.py, sideways_wolf.py

CREATE INVENTORY:
List all found files with:
- Full path
- File size
- Last modified date
- Quick grep for key classes/functions

SEARCH COMMANDS:
find ~ -name "*rick*.py" -o -name "*wolf*.py" -o -name "*charter*.py" 2>/dev/null
find ~ -name "*guardian*.py" -o -name "*regime*.py" -o -name "*canary*.py" 2>/dev/null
grep -r "class.*WolfPack" ~ --include="*.py" 2>/dev/null
grep -r "PIN.*841921" ~ --include="*.py" 2>/dev/null
```

---

### Phase 2: Extract and Combine Foundation Layer

**VSCode Agent Prompt:**
```
TASK: Assemble foundation/rick_charter.py from found code

SEARCH FOR:
1. Files containing "class RICKCharter" or "PIN = 841921"
2. Charter constants: MAX_HOLD_HOURS, MIN_RISK_REWARD, ALLOWED_TIMEFRAMES

COMBINE STRATEGY:
- If multiple files found, merge the BEST version
- Remove TA-Lib imports (import talib) - REPLACE with pure Python
- Remove pandas_ta imports - REPLACE with pure Python
- Keep only: numpy, pandas (built-in functions)

PYTHON REPLACEMENTS (NO TA-LIB):
# INSTEAD OF: import talib
# USE: Pure Python calculations

RSI Calculation (Pure Python):
```python
def calculate_rsi(prices, period=14):
    """Pure Python RSI - no TA-Lib"""
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

MACD Calculation (Pure Python):
```python
def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Pure Python MACD - no TA-Lib"""
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_values = [sum(data[:period]) / period]
        for price in data[period:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values[-1]
    
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    macd_line = fast_ema - slow_ema
    return macd_line
```

Bollinger Bands (Pure Python):
```python
def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Pure Python Bollinger Bands - no TA-Lib"""
    import statistics
    recent = prices[-period:]
    middle = sum(recent) / len(recent)
    std = statistics.stdev(recent)
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower
```

CREATE: foundation/rick_charter.py
- Include Charter PIN 841921
- All constants defined
- No external TA libraries
```

---

### Phase 3: Assemble Hive Gatekeeping Layer

**VSCode Agent Prompt:**
```
TASK: Combine hive layer from multiple sources

LOCATE FILES:
- guardian_gates.py (4-gate validation)
- crypto_entry_gate_system.py (crypto gates)
- quant_hedge_rules.py (hedge logic)

BASH COMMANDS TO FIND:
grep -r "def validate_trade" ~ --include="*.py" 2>/dev/null
grep -r "class GuardianGates" ~ --include="*.py" 2>/dev/null
grep -r "def check_crypto_entry" ~ --include="*.py" 2>/dev/null

COMBINE STRATEGY:
1. Find best version of each file
2. Remove TA-Lib dependencies
3. Ensure 4 gates exist:
   - Gate 1: Timeframe validation
   - Gate 2: Notional size check
   - Gate 3: Risk/Reward ratio
   - Gate 4: Hold time limit

PURE PYTHON ONLY:
- Replace any talib.* calls
- Use statistics module for std dev
- Use math module for calculations
- Use list comprehensions for moving averages

CREATE: hive/guardian_gates.py
CREATE: hive/crypto_entry_gate_system.py
CREATE: hive/quant_hedge_rules.py
```

---

### Phase 4: Assemble Logic Layer

**VSCode Agent Prompt:**
```
TASK: Build logic layer from existing code

LOCATE FILES:
- regime_detector.py (market regime classification)
- smart_logic.py (signal confluence)

BASH COMMANDS:
find ~ -name "*regime*.py" -exec grep -l "BULLISH\|BEARISH\|SIDEWAYS" {} \; 2>/dev/null
find ~ -name "*smart*.py" -exec grep -l "signal.*score\|confluence" {} \; 2>/dev/null

REGIME DETECTION (Pure Python):
```python
def detect_regime(market_data):
    """Pure Python regime detection - no TA-Lib"""
    prices = market_data['close']
    
    # Simple trend detection
    ma_short = sum(prices[-10:]) / 10
    ma_long = sum(prices[-50:]) / 50
    trend = (ma_short - ma_long) / ma_long * 100
    
    # Simple volatility
    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    volatility = (sum([r**2 for r in returns[-20:]]) / 20) ** 0.5
    
    # Classify regime
    if trend > 2 and volatility < 0.02:
        return "BULLISH"
    elif trend < -2 and volatility < 0.02:
        return "BEARISH"
    elif abs(trend) < 1 and volatility < 0.015:
        return "SIDEWAYS"
    elif volatility > 0.03:
        return "CRASH"
    else:
        return "SIDEWAYS"
```

CREATE: logic/regime_detector.py (NO TA-LIB)
CREATE: logic/smart_logic.py (NO TA-LIB)
```

---

### Phase 5: Assemble Wolf Pack Strategies

**VSCode Agent Prompt:**
```
TASK: Combine Wolf Pack strategies from multiple repos

LOCATE FILES:
- bullish_wolf.py
- bearish_wolf.py  
- sideways_wolf.py

BASH COMMANDS:
find ~ -name "*bullish*.py" -o -name "*bearish*.py" -o -name "*sideways*.py" 2>/dev/null
grep -r "class.*WolfPack" ~ --include="*.py" -l 2>/dev/null

FOR EACH WOLF PACK:
1. Find best version across all repos
2. Extract core logic
3. Remove ALL TA-Lib imports
4. Replace with pure Python calculations
5. Ensure Charter compliance

EXAMPLE: Bullish Wolf (Pure Python):
```python
class BullishWolfPack:
    def __init__(self):
        from foundation.rick_charter import RICKCharter
        from hive.guardian_gates import GuardianGates
        self.charter = RICKCharter()
        self.gates = GuardianGates()
    
    def calculate_rsi_score(self, prices):
        """Pure Python RSI - NO TA-LIB"""
        rsi = self._pure_rsi(prices)
        return 0.25 if 30 <= rsi <= 70 else 0.0
    
    def calculate_bb_score(self, prices):
        """Pure Python BB - NO TA-LIB"""
        upper, middle, lower = self._pure_bb(prices)
        current = prices[-1]
        return 0.25 if current > middle else 0.0
    
    def calculate_macd_score(self, prices):
        """Pure Python MACD - NO TA-LIB"""
        macd, signal = self._pure_macd(prices)
        return 0.30 if macd > signal else 0.0
    
    def calculate_volume_score(self, volumes):
        """Pure Python Volume - NO TA-LIB"""
        current = volumes[-1]
        avg = sum(volumes[-20:]) / 20
        return 0.20 if current > avg else 0.0
    
    def _pure_rsi(self, prices, period=14):
        # Pure Python implementation
        pass
    
    def _pure_bb(self, prices, period=20):
        # Pure Python implementation
        pass
    
    def _pure_macd(self, prices):
        # Pure Python implementation
        pass
```

CREATE: strategies/bullish_wolf.py (NO TA-LIB)
CREATE: strategies/bearish_wolf.py (NO TA-LIB)
CREATE: strategies/sideways_wolf.py (NO TA-LIB)
```

---

### Phase 6: Assemble Trading Engines

**VSCode Agent Prompt:**
```
TASK: Combine trading engines from repos

LOCATE FILES:
- ghost_trading_charter_compliant.py
- canary_trading_engine.py
- capital_manager.py

BASH COMMANDS:
find ~ -name "*ghost*.py" -o -name "*canary*.py" 2>/dev/null
grep -r "class.*Engine" ~ --include="*.py" 2>/dev/null

INTEGRATION PATTERN:
```python
# canary_trading_engine.py (Pure Python)
from logic.regime_detector import RegimeDetector
from strategies.bullish_wolf import BullishWolfPack
from strategies.bearish_wolf import BearishWolfPack
from strategies.sideways_wolf import SidewaysWolfPack

class CanaryTradingEngine:
    def __init__(self):
        self.regime_detector = RegimeDetector()
        self.strategies = {
            'BULLISH': BullishWolfPack(),
            'BEARISH': BearishWolfPack(),
            'SIDEWAYS': SidewaysWolfPack()
        }
    
    def process_signal(self, market_data):
        # Detect regime (pure Python)
        regime = self.regime_detector.detect_regime(market_data)
        
        # Select strategy
        strategy = self.strategies.get(regime)
        if not strategy or regime == 'CRASH':
            return {'action': 'HOLD'}
        
        # Check entry (pure Python calculations)
        valid, score = strategy.check_entry_conditions(market_data)
        
        # Rest of logic...
```

CREATE: ghost_trading_charter_compliant.py (NO TA-LIB)
CREATE: canary_trading_engine.py (NO TA-LIB)
CREATE: capital_manager.py (NO TA-LIB)
```

---

### Phase 7: Assemble Risk & Broker Layers

**VSCode Agent Prompt:**
```
TASK: Combine risk management and broker files

LOCATE:
- risk/dynamic_sizing.py
- risk/session_breaker.py
- brokers/oanda_connector.py

BASH COMMANDS:
find ~ -path "*/risk/*.py" 2>/dev/null
find ~ -path "*/brokers/*.py" 2>/dev/null

PURE PYTHON ONLY:
- No TA-Lib for volatility calculations
- Use statistics.stdev() for standard deviation
- Use math functions for ATR calculations

ATR (Pure Python):
```python
def calculate_atr(highs, lows, closes, period=14):
    """Pure Python ATR - NO TA-LIB"""
    true_ranges = []
    for i in range(1, len(closes)):
        hl = highs[i] - lows[i]
        hc = abs(highs[i] - closes[i-1])
        lc = abs(lows[i] - closes[i-1])
        true_ranges.append(max(hl, hc, lc))
    
    return sum(true_ranges[-period:]) / period
```

CREATE: risk/dynamic_sizing.py (NO TA-LIB)
CREATE: risk/session_breaker.py (NO TA-LIB)
CREATE: brokers/oanda_connector.py (NO TA-LIB)
```

---

## 🔄 FRANKENSTEIN ASSEMBLY PROCESS

**VSCode Agent Complete Workflow:**

```
STEP 1: INVENTORY
Run bash commands to find all RICK files across:
- Local repos: /home/ing/RICK/*
- GitHub repos: clone and search
- Other locations: search entire home directory

STEP 2: PRIORITIZE
For each component, rank found files by:
1. Most recent modification date
2. Largest file size (more complete)
3. Contains Charter PIN 841921
4. Has fewer external dependencies

STEP 3: EXTRACT
For each component:
1. Copy the BEST version
2. Remove TA-Lib imports: import talib → DELETE
3. Remove pandas_ta imports: import pandas_ta → DELETE
4. Replace with pure Python equivalents
5. Keep imports: numpy, pandas, statistics, math

STEP 4: COMBINE
Create final files in this repo:
foundation/rick_charter.py
hive/guardian_gates.py
hive/crypto_entry_gate_system.py
hive/quant_hedge_rules.py
logic/regime_detector.py
logic/smart_logic.py
strategies/bullish_wolf.py
strategies/bearish_wolf.py
strategies/sideways_wolf.py
ghost_trading_charter_compliant.py
canary_trading_engine.py
capital_manager.py
risk/dynamic_sizing.py
risk/session_breaker.py
brokers/oanda_connector.py

STEP 5: VERIFY
Run: bash scripts/verify_and_activate_all_systems.sh
Should show 100% after assembly

STEP 6: TEST
python3 -c "from foundation.rick_charter import RICKCharter; print('OK')"
python3 -c "from strategies.bullish_wolf import BullishWolfPack; print('OK')"
python3 canary_trading_engine.py --test
```

---

## 📋 PURE PYTHON TECHNICAL INDICATORS LIBRARY

**Include this in a utils/indicators.py file:**

```python
"""
Pure Python Technical Indicators - NO TA-LIB
Use these instead of talib.* functions
"""

import statistics
import math

def sma(prices, period):
    """Simple Moving Average"""
    return sum(prices[-period:]) / period

def ema(prices, period):
    """Exponential Moving Average"""
    multiplier = 2 / (period + 1)
    ema_val = sma(prices[:period], period)
    for price in prices[period:]:
        ema_val = (price - ema_val) * multiplier + ema_val
    return ema_val

def rsi(prices, period=14):
    """Relative Strength Index"""
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(prices, fast=12, slow=26, signal=9):
    """MACD Indicator"""
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema([macd_line] * signal, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def bollinger_bands(prices, period=20, std_dev=2):
    """Bollinger Bands"""
    recent = prices[-period:]
    middle = sum(recent) / len(recent)
    std = statistics.stdev(recent)
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower

def atr(highs, lows, closes, period=14):
    """Average True Range"""
    true_ranges = []
    for i in range(1, len(closes)):
        hl = highs[i] - lows[i]
        hc = abs(highs[i] - closes[i-1])
        lc = abs(lows[i] - closes[i-1])
        true_ranges.append(max(hl, hc, lc))
    return sum(true_ranges[-period:]) / period

def stochastic(highs, lows, closes, period=14):
    """Stochastic Oscillator"""
    recent_high = max(highs[-period:])
    recent_low = min(lows[-period:])
    current = closes[-1]
    
    if recent_high == recent_low:
        return 50
    
    k = 100 * (current - recent_low) / (recent_high - recent_low)
    return k
```

---

## 🚀 FINAL VSCode AGENT COMMAND

**Complete assembly prompt:**

```
TASK: Assemble RICK trading system from my existing code

REQUIREMENTS:
1. NO TA-LIB - Pure Python only
2. Search local repos: /home/ing/RICK/*
3. Search my GitHub repos for RICK components
4. Combine best versions from multiple sources
5. Replace all TA-Lib calls with pure Python
6. Ensure Charter PIN 841921 compliance
7. Verify all 4 Guardian Gates work

STEPS:
1. Run search commands to inventory all files
2. For each component, select best version
3. Remove external dependencies (TA-Lib, pandas_ta)
4. Replace with pure Python calculations
5. Create utils/indicators.py with pure Python functions
6. Test all imports work
7. Run verification script

DELIVERABLES:
- All 15+ components assembled
- 100% pure Python (no TA-Lib)
- Passes verification script
- Ready to activate Canary

TIMELINE: 2-3 hours (Frankenstein assembly from existing code)

START NOW.
```

---

## ✅ VERIFICATION COMMANDS

After VSCode agent completes assembly:

```bash
# Check no TA-Lib imports remain
grep -r "import talib" . --include="*.py"
# Should return nothing

grep -r "import pandas_ta" . --include="*.py"
# Should return nothing

# Verify pure Python only
grep -r "^import " . --include="*.py" | grep -v "numpy\|pandas\|statistics\|math\|datetime\|json\|os\|sys"

# Test imports
python3 -c "from foundation.rick_charter import RICKCharter; print('✓ Charter')"
python3 -c "from hive.guardian_gates import GuardianGates; print('✓ Gates')"
python3 -c "from logic.regime_detector import RegimeDetector; print('✓ Regime')"
python3 -c "from strategies.bullish_wolf import BullishWolfPack; print('✓ Wolf')"

# Run full verification
bash scripts/verify_and_activate_all_systems.sh
# Should show 100%

# Activate
python3 canary_trading_engine.py --test
```

---

**Time saved:** Weeks → Hours (using existing code + Frankenstein assembly)
**No TA-Lib:** All pure Python implementations provided
**VSCode Agent:** Complete instructions for automated assembly
