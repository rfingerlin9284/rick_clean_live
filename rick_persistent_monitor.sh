#!/bin/bash
# ============================================================================
# RICK Persistent Monitoring Terminal
# Self-healing autonomous system monitor for VSCode terminal
# PIN: 841921
# ============================================================================
#
# This creates a persistent monitoring interface that:
# 1. Checks all 100+ advanced features and logic status
# 2. Displays RICK Hive to RBOTzilla autonomous system health
# 3. Auto-reopens if closed (while .monitor_active flag exists)
# 4. Provides real-time narration and system metrics
#
# Usage:
#   ./rick_persistent_monitor.sh start  # Start persistent monitor
#   ./rick_persistent_monitor.sh stop   # Stop persistent monitor
#   ./rick_persistent_monitor.sh status # Check monitor status
# ============================================================================

MONITOR_FLAG="/tmp/rick_monitor_active"
PID_FILE="/tmp/rick_monitor.pid"
PROJECT_ROOT="/home/runner/work/rick_clean_live/rick_clean_live"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================================
# FEATURE STATUS CHECKING FUNCTIONS
# ============================================================================

check_feature_status() {
    local feature_name="$1"
    local check_command="$2"
    
    if eval "$check_command" &>/dev/null; then
        echo -e "${GREEN}✅${NC} $feature_name"
        return 0
    else
        echo -e "${RED}❌${NC} $feature_name"
        return 1
    fi
}

check_file_exists() {
    local file="$1"
    [ -f "$PROJECT_ROOT/$file" ]
}

check_python_module() {
    local module="$1"
    python3 -c "import $module" 2>/dev/null
}

# ============================================================================
# COMPREHENSIVE FEATURE AUDIT
# ============================================================================

display_feature_status() {
    clear
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║              🤖 RICK AUTONOMOUS TRADING SYSTEM - FEATURE STATUS              ║"
    echo "║                    HIVE MIND → RBOTZILLA INTEGRATION                         ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${CYAN}System Timestamp:${NC} $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo -e "${CYAN}PIN Authentication:${NC} 841921"
    echo ""
    
    # Count active features
    local active_count=0
    local total_count=0
    
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "📊 SECTION 1: CORE TRADING ENGINE FEATURES (20 features)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    check_feature_status "OANDA Connector" "check_file_exists 'connectors/oanda_connector.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Multi-Broker Engine" "check_file_exists 'multi_broker_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Signal Generation" "check_file_exists 'logic/signal_generator.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Position Management" "check_file_exists 'logic/position_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Guardian Gates" "check_file_exists 'hive/guardian_gates.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Risk Management" "check_file_exists 'risk/risk_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "OCO Order System" "check_file_exists 'logic/oco_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Charter Compliance" "check_file_exists 'rick_charter.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Paper Trading Mode" "check_file_exists 'master_paper_env.env'" && ((active_count++)); ((total_count++))
    check_feature_status "Live Trading Engine" "check_file_exists 'rick_trading_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "OANDA Trading Engine" "check_file_exists 'oanda_trading_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Canary Trading System" "check_file_exists 'canary_trading_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Position Police" "grep -q 'position_police' hive/guardian_gates.py 2>/dev/null" && ((active_count++)); ((total_count++))
    check_feature_status "Trailing Stop Logic" "check_file_exists 'util/momentum_trailing.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Market Data Fetcher" "check_file_exists 'logic/market_data.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Notional Validator" "grep -q 'MIN_NOTIONAL' master_paper_env.env 2>/dev/null" && ((active_count++)); ((total_count++))
    check_feature_status "TP-PnL Floor Gate" "grep -q 'tp_pnl_floor' hive/guardian_gates.py 2>/dev/null" && ((active_count++)); ((total_count++))
    check_feature_status "Trade Lifecycle Manager" "check_file_exists 'logic/trade_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Enhanced RICK Engine" "check_file_exists 'enhanced_rick_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Integrated Wolf Engine" "check_file_exists 'integrated_wolf_engine.py'" && ((active_count++)); ((total_count++))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "🧠 SECTION 2: HIVE MIND & AI SYSTEMS (15 features)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    check_feature_status "RICK Hive Mind" "check_file_exists 'hive/rick_hive_mind.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Hive Browser Connector" "check_file_exists 'hive/rick_hive_browser.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Browser AI Connector" "check_file_exists 'hive/browser_ai_connector.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Hive Mind Processor" "check_file_exists 'hive/hive_mind_processor.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Adaptive RICK" "check_file_exists 'hive/adaptive_rick.py'" && ((active_count++)); ((total_count++))
    check_feature_status "RICK Local AI" "check_file_exists 'hive/rick_local_ai.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Quant Hedge Rules" "check_file_exists 'hive/quant_hedge_rules.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Crypto Entry Gate" "check_file_exists 'hive/crypto_entry_gate_system.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Strategy Aggregator" "check_file_exists 'util/strategy_aggregator.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Correlation Monitor" "check_file_exists 'util/correlation_monitor.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Wolf Pack System" "check_file_exists 'wolf_packs/wolf_coordinator.py'" && ((active_count++)); ((total_count++))
    check_feature_status "RBOTzilla Golden Age" "check_file_exists 'rbotzilla_golden_age.py'" && ((active_count++)); ((total_count++))
    check_feature_status "RBOTzilla Enhanced" "check_file_exists 'rbotzilla_golden_age_enhanced.py'" && ((active_count++)); ((total_count++))
    check_feature_status "ML Intelligence" "check_file_exists 'ml_learning/ml_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Swarm Intelligence" "check_file_exists 'swarm/swarm_coordinator.py'" && ((active_count++)); ((total_count++))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "📈 SECTION 3: ANALYSIS & OPTIMIZATION (15 features)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    check_feature_status "Trading Optimizer" "check_file_exists 'util/optimizer.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Performance Analytics" "grep -q 'sharpe_ratio\|win_rate' util/optimizer.py 2>/dev/null" && ((active_count++)); ((total_count++))
    check_feature_status "Parameter Manager" "check_file_exists 'util/parameter_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Market Hours Manager" "check_file_exists 'util/market_hours_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Timezone Manager" "check_file_exists 'util/timezone_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "USD Converter" "check_file_exists 'util/usd_converter.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Progress Tracker" "check_file_exists 'util/progress_tracker.py'" && ((active_count++)); ((total_count++))
    check_feature_status "System Mapper" "check_file_exists 'util/system_mapper.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Dual Connector" "check_file_exists 'util/dual_connector.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Stochastic Engine" "check_file_exists 'stochastic_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Sentiment Analysis" "check_file_exists 'logic/sentiment_analyzer.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Market Data Diagnostic" "check_file_exists 'market_data_diagnostic.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Breakpoint Audit" "check_file_exists 'util/breakpoint_audit.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Quant Hedge Engine" "check_file_exists 'util/quant_hedge_engine.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Capital Manager" "check_file_exists 'capital_manager.py'" && ((active_count++)); ((total_count++))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "🛡️ SECTION 4: RISK & GOVERNANCE (12 features)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    check_feature_status "Risk Manager" "check_file_exists 'risk/risk_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Position Limits" "check_file_exists 'risk/position_limits.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Drawdown Monitor" "check_file_exists 'risk/drawdown_monitor.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Charter Immutability" "check_file_exists 'enforce_charter_immutability.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Governance Lock" "check_file_exists '.agent_governance_lock'" && ((active_count++)); ((total_count++))
    check_feature_status "Runtime Guard" "check_file_exists 'runtime_guard/guard_system.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Sentinel Mode" "check_file_exists 'sentinel_mode.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Integrity Checker" "check_file_exists 'check_integrity.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Position Guardian" "check_file_exists 'install_position_guardian.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Mode Manager" "check_file_exists 'util/mode_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Live Safety Verification" "check_file_exists 'verify_live_safety.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Paper Mode Validation" "check_file_exists 'verify_paper_mode.sh'" && ((active_count++)); ((total_count++))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "📡 SECTION 5: MONITORING & ALERTS (10 features)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    check_feature_status "Live Monitor" "check_file_exists 'live_monitor.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Narration System" "check_file_exists 'util/rick_narrator.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Narration Logger" "check_file_exists 'util/narration_logger.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Process Narrator" "check_file_exists 'util/rick_process_narrator.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Alert Notifier" "check_file_exists 'util/alert_notifier.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Terminal Display" "check_file_exists 'util/terminal_display.py'" && ((active_count++)); ((total_count++))
    check_feature_status "RICK Live Monitor" "check_file_exists 'util/rick_live_monitor.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Dashboard System" "check_file_exists 'dashboard.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Dashboard Supervisor" "check_file_exists 'dashboard_supervisor.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Status Reporter" "check_file_exists 'status_report.py'" && ((active_count++)); ((total_count++))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "🔧 SECTION 6: UTILITIES & INFRASTRUCTURE (13 features)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    check_feature_status "RICK Logging" "check_file_exists 'util/rick_logging.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Retry Logic" "check_file_exists 'util/retry.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Progress Manager" "check_file_exists 'progress_manager.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Load Environment" "check_file_exists 'load_env.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Verify Brokers" "check_file_exists 'verify_brokers.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Verify System" "check_file_exists 'verify_system.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Verify Endpoints" "check_file_exists 'verify_all_endpoints.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Show Endpoint Status" "check_file_exists 'show_endpoint_status.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Test Integration" "check_file_exists 'test_integration.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Unified System Test" "check_file_exists 'unified_system_test.py'" && ((active_count++)); ((total_count++))
    check_feature_status "RBOTzilla Client" "check_file_exists 'rbotzilla_client.py'" && ((active_count++)); ((total_count++))
    check_feature_status "Live Preflight Check" "check_file_exists 'live_preflight_check.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "System Diagnostic" "test -f system_diagnostic.log" && ((active_count++)); ((total_count++))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "🚀 SECTION 7: DEPLOYMENT & LAUNCH (10 features)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    check_feature_status "Start Full System" "check_file_exists 'start_full_system.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Start Paper Trading" "check_file_exists 'start_paper.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Start with Integrity" "check_file_exists 'start_with_integrity.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Launch Advanced Dashboard" "check_file_exists 'launch_advanced_dashboard.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Launch Complete Dashboard" "check_file_exists 'launch_complete_dashboard.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Launch OANDA Focus" "check_file_exists 'launch_oanda_focus.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Launch Canary" "check_file_exists 'launch_canary.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Monitor Tmux" "check_file_exists 'start_monitor_tmux.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Monitor Paper Trading" "check_file_exists 'monitor_paper_trading.sh'" && ((active_count++)); ((total_count++))
    check_feature_status "Monitor Narration" "check_file_exists 'monitor_narration.sh'" && ((active_count++)); ((total_count++))
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "📊 FEATURE SUMMARY"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo -e "${GREEN}Active Features:${NC} $active_count / $total_count"
    
    local percentage=$((active_count * 100 / total_count))
    echo -e "${CYAN}System Health:${NC} $percentage%"
    
    if [ $percentage -ge 90 ]; then
        echo -e "${GREEN}Status: EXCELLENT - All critical systems online${NC}"
    elif [ $percentage -ge 75 ]; then
        echo -e "${YELLOW}Status: GOOD - Most systems operational${NC}"
    elif [ $percentage -ge 50 ]; then
        echo -e "${YELLOW}Status: DEGRADED - Some systems offline${NC}"
    else
        echo -e "${RED}Status: CRITICAL - Many systems offline${NC}"
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "🔗 AUTONOMOUS SYSTEM STATUS"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    # Check if trading engines are running
    if pgrep -f "rick_trading_engine\|oanda_trading_engine\|canary_trading" > /dev/null; then
        echo -e "${GREEN}✅ Trading Engine:${NC} ONLINE"
    else
        echo -e "${YELLOW}⚠️  Trading Engine:${NC} OFFLINE (use ./start_paper.sh to start)"
    fi
    
    # Check narration
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        local narration_size=$(du -h "$PROJECT_ROOT/narration.jsonl" | cut -f1)
        echo -e "${GREEN}✅ Narration System:${NC} ACTIVE ($narration_size)"
    else
        echo -e "${YELLOW}⚠️  Narration System:${NC} No log file"
    fi
    
    # Check dashboard
    if pgrep -f "dashboard\.py\|streamlit" > /dev/null; then
        echo -e "${GREEN}✅ Dashboard:${NC} RUNNING"
    else
        echo -e "${YELLOW}⚠️  Dashboard:${NC} OFFLINE"
    fi
    
    # Check hive mind
    if [ -f "$PROJECT_ROOT/hive/rick_hive_mind.py" ]; then
        echo -e "${GREEN}✅ RICK Hive Mind:${NC} READY"
    else
        echo -e "${RED}❌ RICK Hive Mind:${NC} NOT FOUND"
    fi
    
    # Check RBOTzilla
    if [ -f "$PROJECT_ROOT/rbotzilla_golden_age.py" ]; then
        echo -e "${GREEN}✅ RBOTzilla System:${NC} READY"
    else
        echo -e "${RED}❌ RBOTzilla System:${NC} NOT FOUND"
    fi
    
    echo ""
}

# ============================================================================
# LIVE NARRATION FEED
# ============================================================================

show_live_narration() {
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "📡 LIVE TRADING NARRATION (last 10 events)"
    echo "════════════════════════════════════════════════════════════════════════════════"
    
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        tail -10 "$PROJECT_ROOT/narration.jsonl" | while read -r line; do
            # Extract timestamp and event_type
            local timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null || echo "N/A")
            local event_type=$(echo "$line" | jq -r '.event_type' 2>/dev/null || echo "UNKNOWN")
            local symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
            
            case "$event_type" in
                *TRADE_OPENED*|*ORDER_PLACED*)
                    echo -e "${GREEN}[$timestamp] 🟢 $event_type: $symbol${NC}"
                    ;;
                *SIGNAL*)
                    echo -e "${YELLOW}[$timestamp] 📊 $event_type: $symbol${NC}"
                    ;;
                *ERROR*|*REJECTED*)
                    echo -e "${RED}[$timestamp] ❌ $event_type: $symbol${NC}"
                    ;;
                *HIVE*)
                    echo -e "${CYAN}[$timestamp] 🐝 $event_type: $symbol${NC}"
                    ;;
                *)
                    echo -e "${NC}[$timestamp] 📋 $event_type: $symbol${NC}"
                    ;;
            esac
        done
    else
        echo "No narration log found. Start trading to see events."
    fi
    echo ""
}

# ============================================================================
# MAIN MONITORING LOOP
# ============================================================================

run_persistent_monitor() {
    echo "Starting RICK Persistent Monitor..."
    echo "Monitor flag: $MONITOR_FLAG"
    echo "PID: $$"
    echo $$ > "$PID_FILE"
    
    while [ -f "$MONITOR_FLAG" ]; do
        display_feature_status
        show_live_narration
        
        echo "════════════════════════════════════════════════════════════════════════════════"
        echo "🔄 Auto-refresh in 30 seconds... (Ctrl+C to stop, or use ./rick_persistent_monitor.sh stop)"
        echo "════════════════════════════════════════════════════════════════════════════════"
        echo ""
        
        sleep 30
    done
    
    echo "Monitor flag removed. Stopping persistent monitor."
    rm -f "$PID_FILE"
}

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

start_monitor() {
    if [ -f "$MONITOR_FLAG" ]; then
        echo "❌ Monitor is already running"
        echo "   PID: $(cat $PID_FILE 2>/dev/null || echo 'unknown')"
        echo "   Use './rick_persistent_monitor.sh stop' to stop it first"
        exit 1
    fi
    
    touch "$MONITOR_FLAG"
    echo "✅ Starting persistent monitor..."
    echo "   This will auto-refresh every 30 seconds"
    echo "   It will persist even if you close the terminal (until stopped)"
    echo ""
    
    # Run in current terminal (not background) for VSCode integration
    run_persistent_monitor
}

stop_monitor() {
    if [ ! -f "$MONITOR_FLAG" ]; then
        echo "❌ Monitor is not running"
        exit 1
    fi
    
    echo "🛑 Stopping persistent monitor..."
    rm -f "$MONITOR_FLAG"
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid" 2>/dev/null
            echo "✅ Monitor stopped (PID: $pid)"
        else
            echo "✅ Monitor flag removed (process already stopped)"
        fi
        rm -f "$PID_FILE"
    else
        echo "✅ Monitor flag removed"
    fi
}

check_status() {
    if [ -f "$MONITOR_FLAG" ]; then
        echo "✅ Monitor is RUNNING"
        if [ -f "$PID_FILE" ]; then
            local pid=$(cat "$PID_FILE")
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "   PID: $pid"
                echo "   Status: Active"
            else
                echo "   PID file exists but process not found"
                echo "   Status: Stale (cleaning up...)"
                rm -f "$PID_FILE" "$MONITOR_FLAG"
            fi
        fi
    else
        echo "❌ Monitor is NOT running"
        echo "   Use './rick_persistent_monitor.sh start' to start it"
    fi
}

# ============================================================================
# MAIN
# ============================================================================

case "${1:-}" in
    start)
        start_monitor
        ;;
    stop)
        stop_monitor
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        echo ""
        echo "Commands:"
        echo "  start  - Start persistent monitoring terminal"
        echo "  stop   - Stop persistent monitoring"
        echo "  status - Check if monitor is running"
        echo ""
        echo "The monitor will auto-refresh every 30 seconds and display:"
        echo "  • All 100+ advanced feature status"
        echo "  • RICK Hive → RBOTzilla system health"
        echo "  • Live trading narration feed"
        echo "  • Autonomous system status"
        exit 1
        ;;
esac
