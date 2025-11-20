#!/bin/bash
cd "$(dirname "$0")/.."

echo "RICK LIVE NARRATION — PLAIN ENGLISH"
echo "==================================="
echo "Ctrl+C stops THIS view only (bot keeps running)"
echo

tail -F narration.jsonl 2>/dev/null | while read -r line; do
  [ -z "$line" ] && continue

  event=$(echo "$line" | jq -r '.event_type // "UNKNOWN"')
  details=$(echo "$line" | jq -c '.details // {}')
  symbol=$(echo "$line" | jq -r '.symbol // ""')
  side=$(echo "$details" | jq -r '.side // ""' | tr 'a-z' 'A-Z')
  entry=$(echo "$details" | jq -r '.entry_price // .entry // ""')
  tp=$(echo "$details" | jq -r '.tp_price // .tp // ""')
  sl=$(echo "$details" | jq -r '.sl_price // .sl // ""')
  pnl=$(echo "$details" | jq -r '.pnl // ""')
  capital=$(echo "$details" | jq -r '.capital // ""')
  cycle=$(echo "$details" | jq -r '.cycle // ""')

  case "$event" in
    "TRADE_OPENED"|"TRADE_EXECUTED")
      echo "RICK: $side $symbol @ $entry  TP=$tp  SL=$sl"
      ;;
    "TRADE_CLOSED"|"POSITION_CLOSED")
      echo "RICK: Closed $symbol — PnL \$${pnl}"
      ;;
    "REAL_LIVE_TRADING_STARTED"|"REAL_PAPER_TRADING_STARTED")
      echo "RICK: LIVE engine engaged — brokers: $(echo "$details" | jq -r '.brokers // "?"'), capital \$${capital}"
      ;;
    "CANARY_SESSION_START")
      echo "RICK: CANARY paper session running — capital \$${capital:-$capital}, rules enforced."
      ;;
    "CYCLE_HEARTBEAT")
      echo "RICK: Heartbeat — capital \$${capital}, cycle ${cycle}"
      ;;
    *)
      echo "RICK: $event — $details"
      ;;
  esac
done
