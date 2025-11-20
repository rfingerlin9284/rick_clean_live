#!/usr/bin/env python3
"""
Test Position Cleanup Functionality
Tests that positions are properly cleaned up when they close,
allowing new trades to be placed.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.resolve()))


def test_check_positions_removes_closed_positions():
    """Test that check_positions removes positions that are no longer open"""
    
    # Mock the required modules
    with patch('oanda_trading_engine.RickCharter') as mock_charter, \
         patch('oanda_trading_engine.OandaConnector') as mock_connector, \
         patch('oanda_trading_engine.TerminalDisplay') as mock_display, \
         patch('oanda_trading_engine.RickNarrator') as mock_narrator, \
         patch('oanda_trading_engine.MarginCorrelationGate') as mock_gate, \
         patch('oanda_trading_engine.log_narration') as mock_log:
        
        # Setup mocks
        mock_charter.validate_pin.return_value = True
        mock_charter.MIN_NOTIONAL_USD = 15000
        mock_charter.MIN_RISK_REWARD_RATIO = 3.2
        mock_charter.DAILY_LOSS_BREAKER_PCT = -5
        mock_charter.MAX_PLACEMENT_LATENCY_MS = 300
        
        mock_connector_instance = Mock()
        mock_connector_instance.account_id = "test_account"
        mock_connector_instance.api_base = "https://api-fxpractice.oanda.com"
        mock_connector.return_value = mock_connector_instance
        
        mock_display_instance = Mock()
        mock_display.return_value = mock_display_instance
        
        # Import after patching
        from oanda_trading_engine import OandaTradingEngine
        
        # Create engine instance
        engine = OandaTradingEngine(environment='practice')
        
        # Add some test positions
        engine.active_positions = {
            'order_1': {
                'symbol': 'EUR_USD',
                'direction': 'BUY',
                'entry': 1.0850,
                'stop_loss': 1.0830,
                'take_profit': 1.0914,
                'units': 14000,
                'timestamp': datetime.now(timezone.utc)
            },
            'order_2': {
                'symbol': 'GBP_USD',
                'direction': 'SELL',
                'entry': 1.2500,
                'stop_loss': 1.2520,
                'take_profit': 1.2436,
                'units': -14000,
                'timestamp': datetime.now(timezone.utc)
            },
            'order_3': {
                'symbol': 'USD_JPY',
                'direction': 'BUY',
                'entry': 150.50,
                'stop_loss': 150.30,
                'take_profit': 151.14,
                'units': 14000,
                'timestamp': datetime.now(timezone.utc)
            }
        }
        
        # Add corresponding active pairs
        engine.active_pairs = {'EUR_USD', 'GBP_USD', 'USD_JPY'}
        
        # Mock get_trades to return only 2 open trades (order_1 and order_3 are still open, order_2 closed)
        mock_connector_instance.get_trades.return_value = [
            {'id': 'order_1', 'instrument': 'EUR_USD'},
            {'id': 'order_3', 'instrument': 'USD_JPY'}
        ]
        
        # Call check_positions
        engine.check_positions()
        
        # Verify that order_2 was removed
        assert 'order_2' not in engine.active_positions, "Closed position should be removed from active_positions"
        assert 'order_1' in engine.active_positions, "Open position should remain in active_positions"
        assert 'order_3' in engine.active_positions, "Open position should remain in active_positions"
        
        # Verify that GBP_USD was removed from active pairs
        assert 'GBP_USD' not in engine.active_pairs, "Closed position's pair should be removed from active_pairs"
        assert 'EUR_USD' in engine.active_pairs, "Open position's pair should remain in active_pairs"
        assert 'USD_JPY' in engine.active_pairs, "Open position's pair should remain in active_pairs"
        
        # Verify that we now have space for new trades
        assert len(engine.active_positions) == 2, "Should have 2 active positions"
        assert len(engine.active_pairs) == 2, "Should have 2 active pairs"
        
        print("✅ Test passed: check_positions correctly removes closed positions")


def test_can_trade_pair_with_available_slots():
    """Test that we can trade a new pair when we have available slots"""
    
    with patch('oanda_trading_engine.RickCharter') as mock_charter, \
         patch('oanda_trading_engine.OandaConnector') as mock_connector, \
         patch('oanda_trading_engine.TerminalDisplay') as mock_display, \
         patch('oanda_trading_engine.RickNarrator') as mock_narrator, \
         patch('oanda_trading_engine.MarginCorrelationGate') as mock_gate:
        
        # Setup mocks
        mock_charter.validate_pin.return_value = True
        mock_charter.MIN_NOTIONAL_USD = 15000
        mock_charter.MIN_RISK_REWARD_RATIO = 3.2
        mock_charter.DAILY_LOSS_BREAKER_PCT = -5
        mock_charter.MAX_PLACEMENT_LATENCY_MS = 300
        
        mock_connector_instance = Mock()
        mock_connector_instance.account_id = "test_account"
        mock_connector_instance.api_base = "https://api-fxpractice.oanda.com"
        mock_connector.return_value = mock_connector_instance
        
        mock_display_instance = Mock()
        mock_display.return_value = mock_display_instance
        
        from oanda_trading_engine import OandaTradingEngine
        
        engine = OandaTradingEngine(environment='practice')
        
        # Add 2 active pairs
        engine.active_pairs = {'EUR_USD', 'GBP_USD'}
        
        # Try to trade a new pair (should succeed since we have 2/4 pairs)
        can_trade, reason = engine._can_trade_pair('USD_JPY')
        
        assert can_trade == True, "Should be able to trade new pair when under limit"
        assert reason == "OK", "Reason should be OK"
        
        print("✅ Test passed: Can trade new pair when under limit")


def test_can_trade_pair_at_limit():
    """Test that we cannot trade a new pair when at the limit"""
    
    with patch('oanda_trading_engine.RickCharter') as mock_charter, \
         patch('oanda_trading_engine.OandaConnector') as mock_connector, \
         patch('oanda_trading_engine.TerminalDisplay') as mock_display, \
         patch('oanda_trading_engine.RickNarrator') as mock_narrator, \
         patch('oanda_trading_engine.MarginCorrelationGate') as mock_gate:
        
        # Setup mocks
        mock_charter.validate_pin.return_value = True
        mock_charter.MIN_NOTIONAL_USD = 15000
        mock_charter.MIN_RISK_REWARD_RATIO = 3.2
        mock_charter.DAILY_LOSS_BREAKER_PCT = -5
        mock_charter.MAX_PLACEMENT_LATENCY_MS = 300
        
        mock_connector_instance = Mock()
        mock_connector_instance.account_id = "test_account"
        mock_connector_instance.api_base = "https://api-fxpractice.oanda.com"
        mock_connector.return_value = mock_connector_instance
        
        mock_display_instance = Mock()
        mock_display.return_value = mock_display_instance
        
        from oanda_trading_engine import OandaTradingEngine
        
        engine = OandaTradingEngine(environment='practice')
        
        # Add 4 active pairs (at the limit)
        engine.active_pairs = {'EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD'}
        
        # Try to trade a new pair (should fail since we're at 4/4 pairs)
        can_trade, reason = engine._can_trade_pair('USD_CAD')
        
        assert can_trade == False, "Should not be able to trade new pair when at limit"
        assert "Platform limit reached" in reason, "Reason should mention platform limit"
        
        print("✅ Test passed: Cannot trade new pair when at limit")


def test_can_retrade_existing_pair():
    """Test that we can trade a pair that's already active"""
    
    with patch('oanda_trading_engine.RickCharter') as mock_charter, \
         patch('oanda_trading_engine.OandaConnector') as mock_connector, \
         patch('oanda_trading_engine.TerminalDisplay') as mock_display, \
         patch('oanda_trading_engine.RickNarrator') as mock_narrator, \
         patch('oanda_trading_engine.MarginCorrelationGate') as mock_gate:
        
        # Setup mocks
        mock_charter.validate_pin.return_value = True
        mock_charter.MIN_NOTIONAL_USD = 15000
        mock_charter.MIN_RISK_REWARD_RATIO = 3.2
        mock_charter.DAILY_LOSS_BREAKER_PCT = -5
        mock_charter.MAX_PLACEMENT_LATENCY_MS = 300
        
        mock_connector_instance = Mock()
        mock_connector_instance.account_id = "test_account"
        mock_connector_instance.api_base = "https://api-fxpractice.oanda.com"
        mock_connector.return_value = mock_connector_instance
        
        mock_display_instance = Mock()
        mock_display.return_value = mock_display_instance
        
        from oanda_trading_engine import OandaTradingEngine
        
        engine = OandaTradingEngine(environment='practice')
        
        # Add 4 active pairs (at the limit)
        engine.active_pairs = {'EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD'}
        
        # Try to trade an existing pair (should succeed even at limit)
        can_trade, reason = engine._can_trade_pair('EUR_USD')
        
        assert can_trade == True, "Should be able to trade existing pair even at limit"
        assert reason == "OK", "Reason should be OK"
        
        print("✅ Test passed: Can retrade existing pair even at limit")


if __name__ == "__main__":
    print("="*60)
    print("Testing Position Cleanup Functionality")
    print("="*60)
    print()
    
    try:
        test_check_positions_removes_closed_positions()
        test_can_trade_pair_with_available_slots()
        test_can_trade_pair_at_limit()
        test_can_retrade_existing_pair()
        
        print()
        print("="*60)
        print("✅ All tests passed!")
        print("="*60)
    except AssertionError as e:
        print()
        print("="*60)
        print(f"❌ Test failed: {e}")
        print("="*60)
        sys.exit(1)
    except Exception as e:
        print()
        print("="*60)
        print(f"❌ Error running tests: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
