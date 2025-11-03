#!/bin/bash
set -e
cd /home/ing/RICK/RICK_LIVE_CLEAN

echo "=== RICK START WITH INTEGRITY (PIN 841921) ==="

# Run integrity check
if ! python3 check_integrity.py; then
    echo "❌ STARTUP BLOCKED: Integrity check failed"
    exit 1
fi

# Load environment
if [ -f .env.oanda_only ]; then
    source .env.oanda_only
elif [ -f .env ]; then
    source .env
fi

# Verify credentials
if [ -z "${OANDA_PRACTICE_TOKEN:-}" ] || [ -z "${OANDA_PRACTICE_ACCOUNT_ID:-}" ]; then
    echo "❌ STARTUP BLOCKED: Missing OANDA credentials"
    exit 2
fi

echo "✓ Integrity validated"
echo "✓ Credentials loaded"
echo "🚀 Starting engine..."

# Start engine
exec python3 -u oanda_trading_engine.py
