#!/bin/bash
# ============================================================================
# RICK Plain English Narration Viewer
# Real-time monitoring of trading activities in human-readable format
# PIN: 841921
# ============================================================================
#
# USAGE:
#   From util directory:    ./plain_english_narration.sh
#   From project root:      ./util/plain_english_narration.sh
#
# DESCRIPTION:
#   Monitors the narration.jsonl file and displays trading events in
#   real-time with color-coded output for easy readability.
#
# FEATURES:
#   - Live streaming of trading events
#   - Color-coded event types (signals, trades, errors, etc.)
#   - Displays last 10 events on startup
#   - Supports all event types: SIGNAL_GENERATED, TRADE_OPENED,
#     TRADE_CLOSED, HIVE_ANALYSIS, RISK_CHECK, and more
#
# REQUIREMENTS:
#   - jq (JSON processor) must be installed
#   - narration.jsonl file must exist (created by trading system)
#
# NOTES:
#   - Press Ctrl+C to stop the viewer
#   - Events are displayed as they occur in real-time
#   - Works with OANDA, Coinbase, and IBKR trading venues
# ============================================================================

# Path to narration log (relative to project root)
NARRATION_LOG="../narration.jsonl"

# Try to find the narration log if not in expected location
if [ ! -f "$NARRATION_LOG" ]; then
    NARRATION_LOG="./narration.jsonl"
fi

if [ ! -f "$NARRATION_LOG" ]; then
    NARRATION_LOG="/home/runner/work/rick_clean_live/rick_clean_live/narration.jsonl"
fi

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🤖 RICK TRADING NARRATION VIEWER                          ║"
echo "║                    Live Trading Activity Monitor                             ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if narration log exists
if [ ! -f "$NARRATION_LOG" ]; then
    echo "❌ Narration log not found at: $NARRATION_LOG"
    echo "   Please ensure the trading system is running and creating narration logs."
    exit 1
fi

echo "📊 Monitoring: $NARRATION_LOG"
echo "Press Ctrl+C to stop"
echo ""
echo "───────────────────────────────────────────────────────────────────────────────"
echo ""

# Function to format timestamp
format_time() {
    echo "$1" | jq -r '.timestamp | split("T")[1] | split("+")[0] | split(".")[0]' 2>/dev/null
}

# Display recent events (last 10) on startup
echo "📜 Recent Events:"
echo ""
tail -10 "$NARRATION_LOG" | while read -r line; do
    event_type=$(echo "$line" | jq -r '.event_type' 2>/dev/null)
    timestamp=$(format_time "$line")
    symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
    venue=$(echo "$line" | jq -r '.venue // "N/A"' 2>/dev/null)
    
    echo "[$timestamp] $event_type | Symbol: $symbol | Venue: $venue"
done

echo ""
echo "───────────────────────────────────────────────────────────────────────────────"
echo "🔴 LIVE FEED (streaming new events):"
echo ""

# Tail with formatted output
tail -F "$NARRATION_LOG" | while read -r line; do
    # Parse event data
    event_type=$(echo "$line" | jq -r '.event_type' 2>/dev/null)
    timestamp=$(format_time "$line")
    symbol=$(echo "$line" | jq -r '.symbol // "N/A"' 2>/dev/null)
    venue=$(echo "$line" | jq -r '.venue // "N/A"' 2>/dev/null)
    
    # Color code and format by event type
    case "$event_type" in
        "SCAN_START")
            pair_count=$(echo "$line" | jq -r '.details.pair_count // "N/A"' 2>/dev/null)
            echo -e "\033[1;36m[$timestamp] 🔍 SCAN_START\033[0m - Scanning $pair_count pairs"
            ;;
        "SIGNAL_GENERATED")
            side=$(echo "$line" | jq -r '.details.side // "N/A"' 2>/dev/null)
            confidence=$(echo "$line" | jq -r '.details.confidence // "N/A"' 2>/dev/null)
            echo -e "\033[1;33m[$timestamp] 📊 SIGNAL: $symbol\033[0m - $side (Confidence: $confidence)"
            ;;
        "SIGNAL_REJECTED")
            reason=$(echo "$line" | jq -r '.details.reason // "N/A"' 2>/dev/null)
            echo -e "\033[1;31m[$timestamp] ❌ REJECTED: $symbol\033[0m - $reason"
            ;;
        "TRADE_OPENED"|"ORDER_PLACED")
            trade_id=$(echo "$line" | jq -r '.details.trade_id // .details.order_id // "N/A"' 2>/dev/null)
            notional=$(echo "$line" | jq -r '.details.notional_usd // "N/A"' 2>/dev/null)
            side=$(echo "$line" | jq -r '.details.side // "N/A"' 2>/dev/null)
            echo -e "\033[1;32m[$timestamp] 🟢 TRADE OPENED: $symbol\033[0m - $side | ID: $trade_id | \$$notional"
            ;;
        "TRADE_CLOSED"|"ORDER_FILLED")
            outcome=$(echo "$line" | jq -r '.details.outcome // "N/A"' 2>/dev/null)
            pnl=$(echo "$line" | jq -r '.details.pnl // "N/A"' 2>/dev/null)
            if [[ "$outcome" == "win" ]] || [[ "$pnl" =~ ^[0-9] ]]; then
                echo -e "\033[1;32m[$timestamp] ✅ TRADE CLOSED: $symbol\033[0m - WIN | P&L: \$$pnl"
            else
                echo -e "\033[1;31m[$timestamp] ❌ TRADE CLOSED: $symbol\033[0m - LOSS | P&L: \$$pnl"
            fi
            ;;
        "POSITION_UPDATE")
            unrealized_pl=$(echo "$line" | jq -r '.details.unrealized_pl // "N/A"' 2>/dev/null)
            echo -e "\033[0;35m[$timestamp] 💹 POSITION: $symbol\033[0m - Unrealized P&L: \$$unrealized_pl"
            ;;
        "RISK_CHECK"|"RISK_VALIDATION")
            status=$(echo "$line" | jq -r '.details.status // "N/A"' 2>/dev/null)
            echo -e "\033[1;35m[$timestamp] 🛡️  RISK CHECK: $symbol\033[0m - $status"
            ;;
        "SESSION_START"|"CANARY_SESSION_START"|"SYSTEM_START")
            echo -e "\033[1;32m[$timestamp] 🚀 SESSION START\033[0m - Venue: $venue"
            echo "$line" | jq -c '.details' 2>/dev/null | head -c 100
            echo ""
            ;;
        "SESSION_END"|"CANARY_SESSION_END"|"SYSTEM_STOP")
            win_rate=$(echo "$line" | jq -r '.details.win_rate // "N/A"' 2>/dev/null)
            total_pnl=$(echo "$line" | jq -r '.details.total_pnl // "N/A"' 2>/dev/null)
            echo -e "\033[1;36m[$timestamp] 🏁 SESSION END\033[0m - Win Rate: $win_rate% | Total P&L: \$$total_pnl"
            ;;
        "ERROR"|"FATAL_ERROR")
            error_msg=$(echo "$line" | jq -r '.details.error // .details.message // "N/A"' 2>/dev/null)
            echo -e "\033[1;31m[$timestamp] ⚠️  ERROR: $symbol\033[0m - $error_msg"
            ;;
        "HIVE_ANALYSIS")
            consensus=$(echo "$line" | jq -r '.details.consensus // "N/A"' 2>/dev/null)
            confidence=$(echo "$line" | jq -r '.details.confidence // "N/A"' 2>/dev/null)
            echo -e "\033[0;36m[$timestamp] 🐝 HIVE ANALYSIS: $symbol\033[0m - $consensus (confidence: $confidence)"
            ;;
        *)
            # Generic event display
            echo -e "\033[0;37m[$timestamp] 📋 $event_type: $symbol\033[0m | Venue: $venue"
            ;;
    esac
done
