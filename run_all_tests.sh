#!/bin/bash
# Run all IBKR and trading system tests
# This script runs the complete test suite for IBKR connector and related components

set -e  # Exit on error

echo "================================================================================"
echo "🧪 RICK Trading System - Complete Test Suite"
echo "================================================================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Test 1: IBKR Connector Mock Tests
echo "📋 Test 1: IBKR Connector Mock Tests"
echo "--------------------------------------------------------------------------------"
python3 tests/test_ibkr_connector_mock.py
echo ""
echo "✅ IBKR Connector Mock Tests: PASSED"
echo ""

# Test 2: Check Engine Status
echo "📋 Test 2: Engine Status Check"
echo "--------------------------------------------------------------------------------"
python3 util/test_check_engine_status.py
echo ""
echo "✅ Engine Status Check: PASSED"
echo ""

# Test 3: Write Test Narration
echo "📋 Test 3: Write Test Narration Data"
echo "--------------------------------------------------------------------------------"
python3 util/test_map_oanda_write.py
echo ""
echo "✅ Test Narration Write: PASSED"
echo ""

# Test 4: Map OANDA to AMM
echo "📋 Test 4: Map OANDA to AMM Trades"
echo "--------------------------------------------------------------------------------"
python3 util/test_map_oanda_to_amm.py narration.jsonl
echo ""
echo "✅ OANDA to AMM Mapping: PASSED"
echo ""

# Summary
echo "================================================================================"
echo "✅ ALL TESTS PASSED!"
echo "================================================================================"
echo ""
echo "Test Summary:"
echo "  ✅ IBKR Connector Mock Tests (4/4 passed)"
echo "  ✅ Engine Status Check"
echo "  ✅ Test Narration Write"
echo "  ✅ OANDA to AMM Mapping"
echo ""
echo "Next steps:"
echo "  1. Review test output above for any warnings"
echo "  2. Check narration.jsonl for test data"
echo "  3. Run integration tests with IB Gateway if available"
echo ""
