#!/bin/bash
# RICK System Complete Verification and Activation Script
# This script implements the full mega prompt verification and activation sequence

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Initialize counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Check function
check_file() {
    local file=$1
    local description=$2
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ -f "$file" ]; then
        log_success "$description: EXISTS"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        log_error "$description: MISSING"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# Check Python import
check_import() {
    local import_stmt=$1
    local description=$2
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if python3 -c "$import_stmt" 2>/dev/null; then
        log_success "$description: LOADABLE"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        log_error "$description: IMPORT FAILED"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# Start verification
clear
echo "=================================="
echo "🚀 RICK SYSTEM VERIFICATION"
echo "=================================="
echo ""

# Get repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

log_info "Repository root: $REPO_ROOT"
echo ""

# PHASE 1: FOUNDATION LAYER
echo "📋 PHASE 1: FOUNDATION LAYER VERIFICATION"
echo "==========================================="

check_file "foundation/rick_charter.py" "Charter Constants"

if [ -f "foundation/rick_charter.py" ]; then
    # Verify Charter PIN
    if grep -q "PIN.*841921" foundation/rick_charter.py; then
        log_success "Charter PIN 841921 verified"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        log_error "Charter PIN 841921 NOT FOUND"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # Verify Charter constants
    for constant in "MAX_HOLD_HOURS" "MIN_RISK_REWARD" "MAX_DAILY_LOSS_PCT" "ALLOWED_TIMEFRAMES" "MIN_NOTIONAL"; do
        if grep -q "$constant" foundation/rick_charter.py; then
            log_success "Charter constant: $constant"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warning "Charter constant missing: $constant"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    done
fi

echo ""

# PHASE 2: HIVE GATEKEEPING LAYER
echo "📋 PHASE 2: HIVE GATEKEEPING LAYER"
echo "==================================="

check_file "hive/guardian_gates.py" "Guardian Gates (4 gates)"
check_file "hive/crypto_entry_gate_system.py" "Crypto Entry Gates"
check_file "hive/quant_hedge_rules.py" "Quant Hedge Rules"

if [ -f "hive/guardian_gates.py" ]; then
    if grep -q "def validate_trade" hive/guardian_gates.py; then
        log_success "Guardian Gates: validate_trade() found"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        log_warning "Guardian Gates: validate_trade() missing"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""

# PHASE 3: LOGIC LAYER
echo "📋 PHASE 3: LOGIC LAYER"
echo "========================"

check_file "logic/regime_detector.py" "Regime Detector"
check_file "logic/smart_logic.py" "Smart Logic Filter"

if [ -f "logic/regime_detector.py" ]; then
    # Check for regime classifications
    for regime in "BULLISH" "BEARISH" "SIDEWAYS" "CRASH"; do
        if grep -q "$regime" logic/regime_detector.py; then
            log_success "Regime: $regime detected"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warning "Regime: $regime not found"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    done
fi

echo ""

# PHASE 4: STRATEGY LAYER (WOLF PACKS)
echo "📋 PHASE 4: STRATEGY LAYER (WOLF PACKS)"
echo "========================================"

check_file "strategies/bullish_wolf.py" "Bullish Wolf Pack"
check_file "strategies/bearish_wolf.py" "Bearish Wolf Pack"
check_file "strategies/sideways_wolf.py" "Sideways Wolf Pack"

# Check for Wolf Pack classes
for wolf in "BullishWolfPack" "BearishWolfPack" "SidewaysWolfPack"; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    found=false
    for file in strategies/*_wolf.py 2>/dev/null; do
        if [ -f "$file" ] && grep -q "class $wolf" "$file"; then
            log_success "Wolf Pack class: $wolf found"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            found=true
            break
        fi
    done
    if [ "$found" = false ]; then
        log_warning "Wolf Pack class: $wolf not found"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
done

echo ""

# PHASE 5: TRADING ENGINES
echo "📋 PHASE 5: TRADING ENGINES"
echo "============================"

check_file "ghost_trading_charter_compliant.py" "Ghost Trading Engine"
check_file "canary_trading_engine.py" "Canary Trading Engine"

# Check for regime integration in canary
if [ -f "canary_trading_engine.py" ]; then
    if grep -q "regime_detector\|RegimeDetector" canary_trading_engine.py; then
        log_success "Canary: Regime detection integrated"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        log_warning "Canary: Regime detection NOT integrated"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # Check for Wolf Pack imports
    for wolf in "bullish_wolf" "bearish_wolf" "sideways_wolf"; do
        if grep -q "$wolf" canary_trading_engine.py; then
            log_success "Canary: $wolf imported"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warning "Canary: $wolf NOT imported"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    done
fi

echo ""

# PHASE 6: RISK MANAGEMENT
echo "📋 PHASE 6: RISK MANAGEMENT"
echo "============================"

check_file "risk/dynamic_sizing.py" "Dynamic Position Sizing"
check_file "risk/session_breaker.py" "Session Circuit Breaker"
check_file "capital_manager.py" "Capital Manager"

echo ""

# PHASE 7: BROKER INTEGRATION
echo "📋 PHASE 7: BROKER INTEGRATION"
echo "==============================="

check_file "brokers/oanda_connector.py" "OANDA Connector"

echo ""

# PHASE 8: PYTHON IMPORT TESTS
echo "📋 PHASE 8: PYTHON IMPORT TESTS"
echo "================================"

log_info "Testing Python imports..."

# Test imports if files exist
if [ -f "foundation/rick_charter.py" ]; then
    check_import "from foundation.rick_charter import RICKCharter" "RICKCharter"
fi

if [ -f "hive/guardian_gates.py" ]; then
    check_import "from hive.guardian_gates import GuardianGates" "GuardianGates"
fi

if [ -f "logic/regime_detector.py" ]; then
    check_import "from logic.regime_detector import RegimeDetector" "RegimeDetector"
fi

if [ -f "strategies/bullish_wolf.py" ]; then
    check_import "from strategies.bullish_wolf import BullishWolfPack" "BullishWolfPack"
fi

if [ -f "strategies/bearish_wolf.py" ]; then
    check_import "from strategies.bearish_wolf import BearishWolfPack" "BearishWolfPack"
fi

if [ -f "strategies/sideways_wolf.py" ]; then
    check_import "from strategies.sideways_wolf import SidewaysWolfPack" "SidewaysWolfPack"
fi

echo ""

# SUMMARY
echo "=========================================="
echo "📊 VERIFICATION SUMMARY"
echo "=========================================="
echo ""
echo "Total Checks:  $TOTAL_CHECKS"
echo -e "${GREEN}Passed:        $PASSED_CHECKS${NC}"
echo -e "${RED}Failed:        $FAILED_CHECKS${NC}"
echo ""

PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
echo "Pass Rate:     $PASS_RATE%"
echo ""

# Determine overall status
if [ $FAILED_CHECKS -eq 0 ]; then
    log_success "✅ ALL SYSTEMS VERIFIED - READY FOR ACTIVATION"
    echo ""
    echo "=========================================="
    echo "🚀 ACTIVATION SEQUENCE"
    echo "=========================================="
    echo ""
    log_info "All components verified. System is ready for activation."
    log_info "To activate trading systems, run:"
    echo ""
    echo "  python3 canary_trading_engine.py --continuous"
    echo ""
    log_warning "CAUTION: Ensure proper configuration before live trading"
    exit 0
elif [ $PASS_RATE -ge 70 ]; then
    log_warning "⚠️  PARTIAL VERIFICATION - Some components missing"
    echo ""
    log_info "Missing components can be created using specifications from:"
    echo "  VSCODE_AGENT_MEGA_PROMPT_RICK_ACTIVATION.md"
    echo ""
    log_info "Critical missing components should be implemented before activation"
    exit 1
else
    log_error "❌ VERIFICATION FAILED - Too many missing components"
    echo ""
    log_error "System is not ready for activation"
    log_info "Please implement missing components according to specifications"
    exit 2
fi
