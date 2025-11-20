#!/usr/bin/env python3
"""
Unit tests for Why No Trade diagnostic tool
PIN: 841921 | Generated: 2025-11-20
"""

import unittest
import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from util.why_no_trade import TradeBlockDiagnostic
from util.positions_registry import PositionsRegistry


class TestWhyNoTrade(unittest.TestCase):
    """Test cases for Why No Trade diagnostic tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_file = os.path.join(self.temp_dir, 'test_registry.json')
        self.narration_file = os.path.join(self.temp_dir, 'test_narration.jsonl')
        
        # Create test narration file with sample violations
        with open(self.narration_file, 'w') as f:
            # Sample charter violation
            f.write(json.dumps({
                'timestamp': '2025-11-20T10:00:00+00:00',
                'event_type': 'CHARTER_VIOLATION',
                'symbol': 'EUR_USD',
                'venue': 'oanda',
                'details': {
                    'violation': 'MIN_NOTIONAL_PRE_ORDER',
                    'notional_usd': 9000,
                    'min_required_usd': 15000
                }
            }) + '\n')
            
            # Another violation
            f.write(json.dumps({
                'timestamp': '2025-11-20T10:05:00+00:00',
                'event_type': 'CHARTER_VIOLATION',
                'symbol': 'GBP_USD',
                'venue': 'oanda',
                'details': {
                    'violation': 'MIN_RR_RATIO',
                    'rr_ratio': 2.5,
                    'min_required': 3.2
                }
            }) + '\n')
        
        # Create diagnostic with custom file paths
        self.diagnostic = TradeBlockDiagnostic(dev_mode=True)
        self.diagnostic.registry = PositionsRegistry(registry_file=self.registry_file)
        self.diagnostic.narration_file = Path(self.narration_file)
    
    def tearDown(self):
        """Clean up test files"""
        for file in [self.registry_file, f"{self.registry_file}.lock", 
                     self.narration_file]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception:
                    pass
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass
    
    def test_check_charter_compliance_notional_ok(self):
        """Test charter compliance check with valid notional"""
        result = self.diagnostic.check_charter_compliance(
            symbol='EUR_USD',
            position_size=15000,
            entry_price=1.0800,
            stop_loss_pips=25,
            take_profit_pips=80
        )
        
        self.assertTrue(result['compliant'])
        self.assertEqual(len(result['violations']), 0)
    
    def test_check_charter_compliance_notional_low(self):
        """Test charter compliance check with low notional"""
        result = self.diagnostic.check_charter_compliance(
            symbol='EUR_USD',
            position_size=5000,  # Too small
            entry_price=1.0800,
            stop_loss_pips=25,
            take_profit_pips=80
        )
        
        self.assertFalse(result['compliant'])
        self.assertTrue(any(v['type'] == 'MIN_NOTIONAL_VIOLATION' for v in result['violations']))
    
    def test_check_charter_compliance_rr_low(self):
        """Test charter compliance check with low R:R ratio"""
        result = self.diagnostic.check_charter_compliance(
            symbol='EUR_USD',
            position_size=15000,
            entry_price=1.0800,
            stop_loss_pips=50,
            take_profit_pips=100  # R:R = 2:1, too low
        )
        
        self.assertFalse(result['compliant'])
        self.assertTrue(any(v['type'] == 'MIN_RR_VIOLATION' for v in result['violations']))
    
    def test_check_registry_block_available(self):
        """Test registry check when symbol is available"""
        result = self.diagnostic.check_registry_block('EUR_USD')
        
        self.assertFalse(result['blocked'])
        self.assertTrue(result.get('available', False))
    
    def test_check_registry_block_in_use(self):
        """Test registry check when symbol is in use"""
        # Register a position
        self.diagnostic.registry.register_position(
            symbol='GBP_USD',
            platform='oanda',
            order_id='12345',
            direction='BUY',
            notional_usd=15000
        )
        
        result = self.diagnostic.check_registry_block('GBP_USD')
        
        self.assertTrue(result['blocked'])
        self.assertEqual(result['reason'], 'SYMBOL_ALREADY_IN_USE')
    
    def test_analyze_recent_violations(self):
        """Test analyzing recent violations from narration file"""
        violations = self.diagnostic.analyze_recent_violations()
        
        self.assertEqual(len(violations), 2)
        self.assertEqual(violations[0]['symbol'], 'GBP_USD')  # Most recent first
        self.assertEqual(violations[1]['symbol'], 'EUR_USD')
    
    def test_analyze_recent_violations_filtered(self):
        """Test analyzing violations filtered by symbol"""
        violations = self.diagnostic.analyze_recent_violations(symbol='EUR_USD')
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]['symbol'], 'EUR_USD')
    
    def test_diagnose_symbol_no_signal(self):
        """Test diagnosing symbol with no active issues"""
        report = self.diagnostic.diagnose_symbol('USD_JPY')
        
        self.assertEqual(report['symbol'], 'USD_JPY')
        self.assertEqual(report['primary_reason'], 'NO_SIGNAL')
        self.assertIn('checks', report)
    
    def test_diagnose_symbol_registry_block(self):
        """Test diagnosing symbol blocked by registry"""
        # Register position
        self.diagnostic.registry.register_position(
            symbol='EUR_USD',
            platform='ibkr',
            order_id='99999',
            direction='BUY',
            notional_usd=20000
        )
        
        report = self.diagnostic.diagnose_symbol('EUR_USD')
        
        self.assertEqual(report['primary_reason'], 'BROKER_REGISTRY_BLOCK')
        self.assertTrue(report['checks']['registry']['blocked'])
    
    def test_diagnose_symbol_recent_violation(self):
        """Test diagnosing symbol with recent violations"""
        report = self.diagnostic.diagnose_symbol('EUR_USD')
        
        # Should find the violation from the test narration file
        self.assertGreater(len(report['checks']['recent_violations']), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestWhyNoTrade))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
