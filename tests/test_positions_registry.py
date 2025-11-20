#!/usr/bin/env python3
"""
Unit tests for Positions Registry
Tests registry functionality, locking, and edge cases.
PIN: 841921 | Generated: 2025-11-20
"""

import unittest
import os
import sys
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from util.positions_registry import PositionsRegistry


class TestPositionsRegistry(unittest.TestCase):
    """Test cases for PositionsRegistry"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use temporary file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.registry_file = os.path.join(self.temp_dir, 'test_registry.json')
        self.registry = PositionsRegistry(registry_file=self.registry_file)
    
    def tearDown(self):
        """Clean up test files"""
        # Remove test files
        for file in [self.registry_file, f"{self.registry_file}.lock", 
                     f"{self.registry_file}.tmp"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception:
                    pass
        
        # Remove temp directory
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass
    
    def test_register_new_position(self):
        """Test registering a new position"""
        result = self.registry.register_position(
            symbol='EUR_USD',
            platform='oanda',
            order_id='12345',
            direction='BUY',
            notional_usd=15000.0
        )
        
        self.assertTrue(result)
        
        # Verify position was registered
        positions = self.registry.get_active_positions()
        self.assertIn('EUR_USD', positions)
        self.assertEqual(positions['EUR_USD']['platform'], 'oanda')
        self.assertEqual(positions['EUR_USD']['order_id'], '12345')
    
    def test_prevent_duplicate_position(self):
        """Test that duplicate positions are prevented"""
        # Register first position
        result1 = self.registry.register_position(
            symbol='GBP_USD',
            platform='oanda',
            order_id='11111',
            direction='BUY',
            notional_usd=15000.0
        )
        self.assertTrue(result1)
        
        # Try to register same symbol on different platform
        result2 = self.registry.register_position(
            symbol='GBP_USD',
            platform='ibkr',
            order_id='22222',
            direction='SELL',
            notional_usd=15000.0
        )
        self.assertFalse(result2)
    
    def test_allow_same_platform_update(self):
        """Test that same platform can update its position"""
        # Register first position
        self.registry.register_position(
            symbol='USD_JPY',
            platform='oanda',
            order_id='33333',
            direction='BUY',
            notional_usd=15000.0
        )
        
        # Update from same platform
        result = self.registry.register_position(
            symbol='USD_JPY',
            platform='oanda',
            order_id='44444',
            direction='SELL',
            notional_usd=20000.0
        )
        self.assertTrue(result)
        
        # Verify update
        positions = self.registry.get_active_positions()
        self.assertEqual(positions['USD_JPY']['order_id'], '44444')
    
    def test_unregister_position(self):
        """Test unregistering a position"""
        # Register position
        self.registry.register_position(
            symbol='EUR_GBP',
            platform='oanda',
            order_id='55555',
            direction='BUY',
            notional_usd=15000.0
        )
        
        # Unregister
        result = self.registry.unregister_position('EUR_GBP', 'oanda')
        self.assertTrue(result)
        
        # Verify removed
        positions = self.registry.get_active_positions()
        self.assertNotIn('EUR_GBP', positions)
    
    def test_unregister_wrong_platform(self):
        """Test that unregister fails with wrong platform"""
        # Register position
        self.registry.register_position(
            symbol='AUD_USD',
            platform='oanda',
            order_id='66666',
            direction='BUY',
            notional_usd=15000.0
        )
        
        # Try to unregister from wrong platform
        result = self.registry.unregister_position('AUD_USD', 'ibkr')
        self.assertFalse(result)
        
        # Verify still exists
        positions = self.registry.get_active_positions()
        self.assertIn('AUD_USD', positions)
    
    def test_is_symbol_available(self):
        """Test checking symbol availability"""
        # Initially available
        self.assertTrue(self.registry.is_symbol_available('NZD_USD'))
        
        # Register position
        self.registry.register_position(
            symbol='NZD_USD',
            platform='oanda',
            order_id='77777',
            direction='BUY',
            notional_usd=15000.0
        )
        
        # Now unavailable
        self.assertFalse(self.registry.is_symbol_available('NZD_USD'))
    
    def test_get_active_positions_all(self):
        """Test getting all active positions"""
        # Register multiple positions
        self.registry.register_position('EUR_USD', 'oanda', '1', 'BUY', 15000)
        self.registry.register_position('GBP_USD', 'ibkr', '2', 'SELL', 20000)
        self.registry.register_position('USD_JPY', 'coinbase', '3', 'BUY', 18000)
        
        positions = self.registry.get_active_positions()
        self.assertEqual(len(positions), 3)
    
    def test_get_active_positions_filtered(self):
        """Test getting positions filtered by platform"""
        # Register positions on different platforms
        self.registry.register_position('EUR_USD', 'oanda', '1', 'BUY', 15000)
        self.registry.register_position('GBP_USD', 'oanda', '2', 'SELL', 20000)
        self.registry.register_position('USD_JPY', 'ibkr', '3', 'BUY', 18000)
        
        # Get only oanda positions
        oanda_positions = self.registry.get_active_positions(platform='oanda')
        self.assertEqual(len(oanda_positions), 2)
        self.assertIn('EUR_USD', oanda_positions)
        self.assertIn('GBP_USD', oanda_positions)
        self.assertNotIn('USD_JPY', oanda_positions)
    
    def test_handle_missing_file(self):
        """Test that missing registry file is handled gracefully"""
        # Registry file doesn't exist yet
        self.assertFalse(os.path.exists(self.registry_file))
        
        # Should still work
        result = self.registry.is_symbol_available('EUR_USD')
        self.assertTrue(result)
        
        # File should be created when registering
        self.registry.register_position('EUR_USD', 'oanda', '1', 'BUY', 15000)
        self.assertTrue(os.path.exists(self.registry_file))
    
    def test_handle_corrupted_file(self):
        """Test that corrupted registry file is handled gracefully"""
        # Create corrupted file
        with open(self.registry_file, 'w') as f:
            f.write('{"invalid json syntax')
        
        # Should handle gracefully and return empty registry
        positions = self.registry.get_active_positions()
        self.assertEqual(len(positions), 0)
        
        # Should be able to register new position
        result = self.registry.register_position('EUR_USD', 'oanda', '1', 'BUY', 15000)
        self.assertTrue(result)
    
    def test_cleanup_stale_positions(self):
        """Test cleanup of stale positions"""
        # Register a position
        self.registry.register_position('EUR_USD', 'oanda', '1', 'BUY', 15000)
        
        # Manually modify timestamp to make it stale
        registry_data = self.registry._load_registry()
        old_time = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat()
        registry_data['positions']['EUR_USD']['registered_at'] = old_time
        self.registry._save_registry(registry_data)
        
        # Cleanup stale positions (older than 1 hour)
        count = self.registry.cleanup_stale_positions(max_age_hours=1)
        self.assertEqual(count, 1)
        
        # Verify position was removed
        positions = self.registry.get_active_positions()
        self.assertNotIn('EUR_USD', positions)
    
    def test_thread_safety(self):
        """Test that registry operations are thread-safe (basic check)"""
        # This is a basic test - full thread safety would require concurrent operations
        # Just verify that lock acquire/release works
        lock_fd = self.registry._acquire_lock(timeout=1)
        self.assertIsNotNone(lock_fd)
        self.registry._release_lock(lock_fd)
        
        # Verify we can acquire again after release
        lock_fd2 = self.registry._acquire_lock(timeout=1)
        self.assertIsNotNone(lock_fd2)
        self.registry._release_lock(lock_fd2)


class TestRegistryEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_file = os.path.join(self.temp_dir, 'test_registry.json')
        self.registry = PositionsRegistry(registry_file=self.registry_file)
    
    def tearDown(self):
        """Clean up test files"""
        for file in [self.registry_file, f"{self.registry_file}.lock", 
                     f"{self.registry_file}.tmp"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception:
                    pass
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass
    
    def test_empty_registry(self):
        """Test operations on empty registry"""
        positions = self.registry.get_active_positions()
        self.assertEqual(len(positions), 0)
        
        available = self.registry.is_symbol_available('EUR_USD')
        self.assertTrue(available)
    
    def test_unregister_nonexistent(self):
        """Test unregistering a position that doesn't exist"""
        result = self.registry.unregister_position('FAKE_SYMBOL', 'oanda')
        self.assertFalse(result)
    
    def test_special_characters_in_symbol(self):
        """Test symbols with special characters"""
        # Some brokers use different formats
        symbols = ['EUR/USD', 'BTC-USD', 'EURUSD']
        
        for symbol in symbols:
            result = self.registry.register_position(
                symbol=symbol,
                platform='test',
                order_id='999',
                direction='BUY',
                notional_usd=15000
            )
            self.assertTrue(result)
            
            # Cleanup for next iteration
            self.registry.unregister_position(symbol, 'test')


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPositionsRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestRegistryEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
