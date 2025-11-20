#!/bin/bash
# RICK Live Narration - Plain English View
# Real-time streaming of trading events without GUI dependencies
# Usage: ./util/plain_english_narration.sh
# Press Ctrl+C to stop this view only (trading bot keeps running)

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NARRATION_FILE="$REPO_ROOT/narration.jsonl"

echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║              RICK LIVE NARRATION — PLAIN ENGLISH — REAL TIME                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Monitoring: $NARRATION_FILE"
echo "⏹️  Press Ctrl+C to stop this view only (bot keeps running)"
echo ""
echo "───────────────────────────────────────────────────────────────────────────────"
echo ""

# Check if narration file exists
if [ ! -f "$NARRATION_FILE" ]; then
    echo "❌ Error: Narration file not found at $NARRATION_FILE"
    echo "   Make sure the trading system is running and generating narration logs."
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ Error: 'jq' is not installed"
    echo "   Install it with: sudo apt-get install jq"
    exit 1
fi

# Stream and format narration events
tail -F "$NARRATION_FILE" | jq -r '
  . as $e
  | .timestamp + " | " + (.event_type // "UNKNOWN") + " | " +
    (.venue // "") + " | " +
    (if .symbol == "SYSTEM" then "" else (.symbol // "") end) + " | " +
    (
      if .event_type == "TRADE_EXECUTED" then
        "trade_id=" + ($e.details.trade_id // "") + " " +
        "side=" + (($e.details.side // "") | ascii_upcase) + " " +
        "entry=" + (($e.details.entry // $e.details.entry_price // "") | tostring) + " " +
        "sl=" + (($e.details.sl // $e.details.sl_price // "") | tostring) + " " +
        "tp=" + (($e.details.tp // $e.details.tp_price // "") | tostring) + " " +
        "wolf=" + ($e.details.wolf_pack // "")
      elif .event_type == "TRADE_OPENED" then
        "trade_id=" + ($e.details.trade_id // "") + " " +
        "side=" + (($e.details.side // "") | ascii_upcase) + " " +
        "notional=" + (($e.details.notional_usd // "") | tostring) + " " +
        "entry=" + (($e.details.entry_price // "") | tostring)
      elif .event_type == "TRADE_CLOSED" then
        "trade_id=" + ($e.details.trade_id // "") + " " +
        "outcome=" + ($e.details.outcome // "") + " " +
        "pnl=" + (($e.details.pnl // "") | tostring) + " " +
        "duration=" + (($e.details.duration_hours // "") | tostring) + "h"
      elif .event_type == "MACHINE_HEARTBEAT" then
        "iteration=" + (($e.details.iteration // 0) | tostring) + " " +
        "regime=" + ($e.details.regime // "") + " " +
        "open_positions=" + (($e.details.open_positions // 0) | tostring) + " " +
        "session_pnl=" + (($e.details.session_pnl // 0) | tostring) + " " +
        "trades_today=" + (($e.details.trades_today // 0) | tostring)
      elif .event_type == "SIGNAL_GENERATED" then
        "side=" + (($e.details.side // "") | ascii_upcase) + " " +
        "rr=" + (($e.details.risk_reward_ratio // "") | tostring) + " " +
        "confidence=" + (($e.details.confidence // "") | tostring)
      elif .event_type == "SIGNAL_REJECTED" then
        "reason=" + ($e.details.reason // "")
      elif .event_type == "HIVE_ANALYSIS" then
        "consensus=" + ($e.details.consensus // "") + " " +
        "confidence=" + (($e.details.confidence // "") | tostring) + " " +
        "order_id=" + ($e.details.order_id // "") + " " +
        "profit_atr=" + (($e.details.profit_atr // "") | tostring)
      elif .event_type == "CANARY_INIT" or .event_type == "CANARY_SESSION_START" or .event_type == "CANARY_SESSION_END" then
        ($e.details | tostring)
      elif .event_type == "TTL_ENFORCEMENT" then
        "duration=" + (($e.details.duration_hours // "") | tostring) + "h " +
        "action=" + ($e.details.action // "")
      else
        ( $e.details | tostring )
      end
    )
'
