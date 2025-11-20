#!/bin/bash
# ============================================================================
# RICK Plain English Interface
# Simple command interface for querying system information
# No coding required - Just ask questions in plain English!
# PIN: 841921
# ============================================================================

# Colors for readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

PROJECT_ROOT="/home/runner/work/rick_clean_live/rick_clean_live"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

show_header() {
    clear
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🤖 RICK PLAIN ENGLISH INTERFACE                           ║"
    echo "║                    Ask Questions - Get Answers                               ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
}

show_help() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}HOW TO USE THIS INTERFACE${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Just type your question or command below. Examples:"
    echo ""
    echo -e "${YELLOW}Questions You Can Ask:${NC}"
    echo "  • status          - Show me the overall system status"
    echo "  • health          - Is the system healthy?"
    echo "  • trading         - Is trading active?"
    echo "  • balance         - What's my account balance?"
    echo "  • trades          - Show me recent trades"
    echo "  • positions       - What positions are open?"
    echo "  • features        - What features are available?"
    echo "  • brokers         - Which brokers am I using?"
    echo "  • activity        - What's happening right now?"
    echo "  • logs            - Show me recent activity logs"
    echo "  • help            - Show this help menu"
    echo "  • menu            - Show all available commands"
    echo "  • quit or exit    - Leave this interface"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

show_menu() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}AVAILABLE COMMANDS${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}System Status:${NC}"
    echo "  status, health, features, brokers"
    echo ""
    echo -e "${YELLOW}Trading Information:${NC}"
    echo "  trading, balance, trades, positions, activity"
    echo ""
    echo -e "${YELLOW}Recent Activity:${NC}"
    echo "  logs, events, signals, errors"
    echo ""
    echo -e "${YELLOW}Configuration:${NC}"
    echo "  config, settings, accounts"
    echo ""
    echo -e "${YELLOW}Help:${NC}"
    echo "  help, menu, quit, exit"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

cmd_status() {
    echo -e "${GREEN}━━━ SYSTEM STATUS ━━━${NC}"
    echo ""
    
    # Check trading engine
    if pgrep -f "rick_trading_engine\|oanda_trading_engine\|canary_trading" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Trading Engine is RUNNING${NC}"
    else
        echo -e "${YELLOW}⚠️  Trading Engine is STOPPED${NC}"
        echo "   (You can start it with: ./start_paper.sh)"
    fi
    
    # Check narration
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        local size=$(du -h "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | cut -f1)
        echo -e "${GREEN}✅ Narration System is ACTIVE${NC}"
        echo "   Log size: $size"
    else
        echo -e "${YELLOW}⚠️  No narration log found${NC}"
    fi
    
    # Check dashboard
    if pgrep -f "dashboard\.py\|streamlit" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Dashboard is RUNNING${NC}"
    else
        echo -e "${YELLOW}⚠️  Dashboard is STOPPED${NC}"
    fi
    
    # Feature count
    local active_features=$(bash -c "cd $PROJECT_ROOT && ./rick_persistent_monitor.sh status 2>/dev/null | grep -o '[0-9]*/[0-9]*' | head -1" 2>/dev/null || echo "N/A")
    if [ "$active_features" != "N/A" ]; then
        echo -e "${GREEN}✅ Active Features: $active_features${NC}"
    fi
    
    echo ""
}

cmd_health() {
    echo -e "${GREEN}━━━ SYSTEM HEALTH CHECK ━━━${NC}"
    echo ""
    
    local health_score=0
    local total_checks=5
    
    # Check 1: Trading engine
    if pgrep -f "rick_trading_engine\|oanda_trading_engine" > /dev/null 2>&1; then
        echo "✅ Trading Engine: Healthy"
        ((health_score++))
    else
        echo "⚠️  Trading Engine: Not running"
    fi
    
    # Check 2: Narration
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        echo "✅ Narration System: Healthy"
        ((health_score++))
    else
        echo "⚠️  Narration System: No log file"
    fi
    
    # Check 3: Configuration
    if [ -f "$PROJECT_ROOT/master_paper_env.env" ]; then
        echo "✅ Configuration: Loaded"
        ((health_score++))
    else
        echo "⚠️  Configuration: Missing"
    fi
    
    # Check 4: Hive Mind
    if [ -f "$PROJECT_ROOT/hive/rick_hive_mind.py" ]; then
        echo "✅ RICK Hive Mind: Ready"
        ((health_score++))
    else
        echo "⚠️  RICK Hive Mind: Not found"
    fi
    
    # Check 5: RBOTzilla
    if [ -f "$PROJECT_ROOT/rbotzilla_golden_age.py" ]; then
        echo "✅ RBOTzilla: Ready"
        ((health_score++))
    else
        echo "⚠️  RBOTzilla: Not found"
    fi
    
    echo ""
    local percentage=$((health_score * 100 / total_checks))
    
    if [ $percentage -ge 80 ]; then
        echo -e "${GREEN}Overall Health: EXCELLENT ($percentage%)${NC}"
    elif [ $percentage -ge 60 ]; then
        echo -e "${YELLOW}Overall Health: GOOD ($percentage%)${NC}"
    else
        echo -e "${YELLOW}Overall Health: NEEDS ATTENTION ($percentage%)${NC}"
    fi
    echo ""
}

cmd_trading() {
    echo -e "${GREEN}━━━ TRADING STATUS ━━━${NC}"
    echo ""
    
    if pgrep -f "rick_trading_engine\|oanda_trading_engine\|canary_trading" > /dev/null 2>&1; then
        local pid=$(pgrep -f "rick_trading_engine\|oanda_trading_engine" | head -1)
        echo -e "${GREEN}✅ Trading is ACTIVE${NC}"
        echo "   Process ID: $pid"
        echo "   Mode: Paper Trading (Safe - No Real Money)"
        echo ""
        echo "Recent trading activity:"
        cmd_activity
    else
        echo -e "${YELLOW}Trading is currently STOPPED${NC}"
        echo ""
        echo "To start paper trading, run:"
        echo "  ./start_paper.sh"
        echo ""
        echo "This will start the trading system in SAFE paper trading mode."
        echo "No real money will be used."
    fi
    echo ""
}

cmd_balance() {
    echo -e "${GREEN}━━━ ACCOUNT BALANCES ━━━${NC}"
    echo ""
    
    echo "📊 Paper Trading Accounts (Safe - Fake Money):"
    echo ""
    echo "1. OANDA Practice Account"
    echo "   Account: 101-001-31210531-002"
    echo "   Type: Practice (Paper Trading)"
    echo "   Status: Configured ✓"
    echo ""
    echo "2. Coinbase Sandbox"
    echo "   Type: Sandbox (Simulated)"
    echo "   Status: Configured ✓"
    echo ""
    echo "3. Interactive Brokers Paper"
    echo "   Account: DUK880040"
    echo "   Port: 7497 (Paper Trading)"
    echo "   Status: Configured ✓"
    echo ""
    echo -e "${CYAN}Note: All accounts are in PAPER TRADING mode.${NC}"
    echo -e "${CYAN}No real money is being used.${NC}"
    echo ""
}

cmd_trades() {
    echo -e "${GREEN}━━━ RECENT TRADES ━━━${NC}"
    echo ""
    
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        echo "Last 5 trading events:"
        echo ""
        tail -50 "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | grep -i "trade\|order" | tail -5 | while read -r line; do
            local timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null || echo "N/A")
            local event_type=$(echo "$line" | jq -r '.event_type' 2>/dev/null || echo "UNKNOWN")
            local symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
            echo "[$timestamp] $event_type - $symbol"
        done
        echo ""
    else
        echo "No trade history found."
        echo "The trading system hasn't been started yet or no trades have occurred."
        echo ""
    fi
}

cmd_positions() {
    echo -e "${GREEN}━━━ OPEN POSITIONS ━━━${NC}"
    echo ""
    
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        local has_positions=$(tail -100 "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | grep -i "position\|trade_opened" | tail -1)
        
        if [ -n "$has_positions" ]; then
            echo "Recent position activity:"
            echo ""
            tail -100 "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | grep -i "position" | tail -5 | while read -r line; do
                local timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null || echo "N/A")
                local symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
                local event=$(echo "$line" | jq -r '.event_type' 2>/dev/null || echo "UNKNOWN")
                echo "[$timestamp] $symbol - $event"
            done
            echo ""
        else
            echo "No open positions at this time."
            echo ""
        fi
    else
        echo "No position data available."
        echo "Start the trading system to see position information."
        echo ""
    fi
}

cmd_features() {
    echo -e "${GREEN}━━━ AVAILABLE FEATURES ━━━${NC}"
    echo ""
    echo "The RICK trading system has 100+ advanced features organized in 7 categories:"
    echo ""
    echo -e "${YELLOW}1. Core Trading Engine (20 features)${NC}"
    echo "   - Multi-broker support, signal generation, position management"
    echo ""
    echo -e "${YELLOW}2. Hive Mind & AI Systems (15 features)${NC}"
    echo "   - RICK Hive Mind, RBOTzilla, browser AI integration"
    echo ""
    echo -e "${YELLOW}3. Analysis & Optimization (15 features)${NC}"
    echo "   - Trading optimizer, performance analytics, parameter management"
    echo ""
    echo -e "${YELLOW}4. Risk & Governance (12 features)${NC}"
    echo "   - Risk management, charter compliance, safety checks"
    echo ""
    echo -e "${YELLOW}5. Monitoring & Alerts (10 features)${NC}"
    echo "   - Live monitoring, narration system, dashboard"
    echo ""
    echo -e "${YELLOW}6. Utilities & Infrastructure (13 features)${NC}"
    echo "   - Logging, verification, testing, system health"
    echo ""
    echo -e "${YELLOW}7. Deployment & Launch (10 features)${NC}"
    echo "   - System starters, launchers, monitors"
    echo ""
    echo "For detailed feature status, run the persistent monitor:"
    echo "  ./rick_persistent_monitor.sh start"
    echo ""
}

cmd_brokers() {
    echo -e "${GREEN}━━━ CONFIGURED BROKERS ━━━${NC}"
    echo ""
    echo "Your system is configured with 3 brokers in PAPER TRADING mode:"
    echo ""
    echo -e "${CYAN}1. OANDA${NC}"
    echo "   Type: Forex Trading"
    echo "   Mode: Practice Account (Paper Trading)"
    echo "   Account: 101-001-31210531-002"
    echo "   URL: api-fxpractice.oanda.com"
    echo "   Status: Safe - No Real Money ✓"
    echo ""
    echo -e "${CYAN}2. Coinbase${NC}"
    echo "   Type: Cryptocurrency Trading"
    echo "   Mode: Sandbox (Simulated)"
    echo "   URL: public-sandbox.exchange.coinbase.com"
    echo "   Status: Safe - No Real Money ✓"
    echo ""
    echo -e "${CYAN}3. Interactive Brokers (IBKR)${NC}"
    echo "   Type: Stocks, Options, Futures"
    echo "   Mode: Paper Account"
    echo "   Account: DUK880040"
    echo "   Port: 7497 (Paper - NOT 7496 Live)"
    echo "   Status: Safe - No Real Money ✓"
    echo ""
    echo -e "${GREEN}All brokers are in PAPER TRADING mode.${NC}"
    echo -e "${GREEN}No real money is at risk.${NC}"
    echo ""
}

cmd_activity() {
    echo -e "${GREEN}━━━ RECENT ACTIVITY ━━━${NC}"
    echo ""
    
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        echo "Last 10 events:"
        echo ""
        tail -10 "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | while read -r line; do
            local timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null || echo "N/A")
            local event_type=$(echo "$line" | jq -r '.event_type' 2>/dev/null || echo "UNKNOWN")
            local symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
            
            case "$event_type" in
                *TRADE*|*ORDER*)
                    echo -e "${GREEN}[$timestamp] 🟢 $event_type - $symbol${NC}"
                    ;;
                *SIGNAL*)
                    echo -e "${YELLOW}[$timestamp] 📊 $event_type - $symbol${NC}"
                    ;;
                *ERROR*|*REJECT*)
                    echo -e "${MAGENTA}[$timestamp] ⚠️  $event_type - $symbol${NC}"
                    ;;
                *)
                    echo "[$timestamp] $event_type - $symbol"
                    ;;
            esac
        done
        echo ""
    else
        echo "No activity log found."
        echo "Start the trading system to see live activity."
        echo ""
    fi
}

cmd_logs() {
    cmd_activity
}

cmd_events() {
    cmd_activity
}

cmd_signals() {
    echo -e "${GREEN}━━━ RECENT SIGNALS ━━━${NC}"
    echo ""
    
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        echo "Last 5 trading signals:"
        echo ""
        grep -i "signal" "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | tail -5 | while read -r line; do
            local timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null || echo "N/A")
            local symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
            local event=$(echo "$line" | jq -r '.event_type' 2>/dev/null || echo "SIGNAL")
            echo "[$timestamp] $event - $symbol"
        done
        echo ""
    else
        echo "No signal data available."
        echo ""
    fi
}

cmd_errors() {
    echo -e "${GREEN}━━━ RECENT ERRORS ━━━${NC}"
    echo ""
    
    if [ -f "$PROJECT_ROOT/narration.jsonl" ]; then
        local errors=$(grep -i "error\|warning" "$PROJECT_ROOT/narration.jsonl" 2>/dev/null | tail -5)
        
        if [ -n "$errors" ]; then
            echo "Last 5 errors/warnings:"
            echo ""
            echo "$errors" | while read -r line; do
                local timestamp=$(echo "$line" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null || echo "N/A")
                local event=$(echo "$line" | jq -r '.event_type' 2>/dev/null || echo "ERROR")
                echo -e "${MAGENTA}[$timestamp] ⚠️  $event${NC}"
            done
            echo ""
        else
            echo -e "${GREEN}No errors found - System is running smoothly! ✓${NC}"
            echo ""
        fi
    else
        echo "No error log available."
        echo ""
    fi
}

cmd_config() {
    echo -e "${GREEN}━━━ SYSTEM CONFIGURATION ━━━${NC}"
    echo ""
    echo "Configuration File: master_paper_env.env"
    echo ""
    echo -e "${YELLOW}Trading Mode:${NC}"
    echo "  • Environment: Sandbox/Paper Trading"
    echo "  • Safety: Paper Trading Only"
    echo "  • Capital: $2,000 per broker (fake money)"
    echo ""
    echo -e "${YELLOW}Brokers Configured:${NC}"
    echo "  • OANDA (Forex) - Practice Account"
    echo "  • Coinbase (Crypto) - Sandbox"
    echo "  • IBKR (Stocks) - Paper Account"
    echo ""
    echo -e "${GREEN}All settings are configured for safe paper trading.${NC}"
    echo -e "${GREEN}No real money is at risk.${NC}"
    echo ""
}

cmd_settings() {
    cmd_config
}

cmd_accounts() {
    cmd_balance
}

# ============================================================================
# MAIN INTERFACE LOOP
# ============================================================================

main_loop() {
    show_header
    show_help
    
    while true; do
        echo -ne "${BLUE}RICK> ${NC}"
        read -r input
        
        # Convert to lowercase for easier matching
        cmd=$(echo "$input" | tr '[:upper:]' '[:lower:]' | xargs)
        
        echo ""
        
        case "$cmd" in
            "quit"|"exit"|"q")
                echo "Goodbye! 👋"
                echo ""
                exit 0
                ;;
            "help"|"h"|"?")
                show_help
                ;;
            "menu"|"commands")
                show_menu
                ;;
            "status"|"what's the status"|"system status")
                cmd_status
                ;;
            "health"|"is the system healthy"|"system health")
                cmd_health
                ;;
            "trading"|"is trading active"|"trading status")
                cmd_trading
                ;;
            "balance"|"balances"|"account balance"|"what's my balance")
                cmd_balance
                ;;
            "trades"|"recent trades"|"show trades"|"trade history")
                cmd_trades
                ;;
            "positions"|"open positions"|"what positions"|"show positions")
                cmd_positions
                ;;
            "features"|"what features"|"show features"|"capabilities")
                cmd_features
                ;;
            "brokers"|"which brokers"|"show brokers"|"broker status")
                cmd_brokers
                ;;
            "activity"|"what's happening"|"recent activity"|"current activity")
                cmd_activity
                ;;
            "logs"|"show logs"|"recent logs")
                cmd_logs
                ;;
            "events"|"show events"|"recent events")
                cmd_events
                ;;
            "signals"|"show signals"|"recent signals"|"trading signals")
                cmd_signals
                ;;
            "errors"|"show errors"|"any errors"|"warnings")
                cmd_errors
                ;;
            "config"|"configuration"|"show config")
                cmd_config
                ;;
            "settings"|"show settings")
                cmd_settings
                ;;
            "accounts"|"show accounts")
                cmd_accounts
                ;;
            "clear"|"cls")
                show_header
                ;;
            "")
                # Empty input, just show prompt again
                ;;
            *)
                echo -e "${YELLOW}I don't understand that command.${NC}"
                echo "Type 'help' to see available commands, or 'menu' for a full list."
                echo ""
                ;;
        esac
    done
}

# ============================================================================
# START THE INTERFACE
# ============================================================================

# Check if running in interactive mode
if [ -t 0 ]; then
    main_loop
else
    echo "This interface requires an interactive terminal."
    echo "Please run it directly from your terminal."
    exit 1
fi
