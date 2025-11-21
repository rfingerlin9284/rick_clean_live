#!/usr/bin/env python3
"""
Test suite for research_strategies package
Validates indicators, patterns, and strategies
PIN: 841921
"""

import sys
import os
import pandas as pd
import numpy as np
import pytest

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from research_strategies import indicators, patterns, regime_features
from research_strategies.trap_reversal_scalper import TrapReversalScalper
from research_strategies.ema_scalper import EMAScalper
from research_strategies.price_action_holy_grail import PriceActionHolyGrail
from research_strategies.fib_confluence import FibConfluence
from research_strategies.pack_manager import StrategyPackManager, create_default_pack_manager


# Test fixtures
@pytest.fixture
def sample_data():
    """Create sample market data for testing"""
    np.random.seed(42)
    n = 300
    
    # Generate realistic price data
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n) * 0.3)
    low = close - np.abs(np.random.randn(n) * 0.3)
    open_ = close + np.random.randn(n) * 0.2
    volume = np.abs(np.random.randn(n) * 1000 + 5000)
    
    dates = pd.date_range('2024-01-01', periods=n, freq='5min')
    
    return pd.DataFrame({
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)


class TestIndicators:
    """Test technical indicators module"""
    
    def test_rsi_calculation(self, sample_data):
        """Test RSI calculation"""
        rsi = indicators.calculate_rsi(sample_data['close'], period=14)
        
        assert not rsi.isna().all(), "RSI should have values"
        assert (rsi.dropna() >= 0).all() and (rsi.dropna() <= 100).all(), "RSI should be 0-100"
        assert len(rsi) == len(sample_data), "RSI length should match data"
    
    def test_atr_calculation(self, sample_data):
        """Test ATR calculation"""
        atr = indicators.calculate_atr(
            sample_data['high'],
            sample_data['low'],
            sample_data['close'],
            period=14
        )
        
        assert not atr.isna().all(), "ATR should have values"
        assert (atr.dropna() >= 0).all(), "ATR should be non-negative"
    
    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation"""
        bb = indicators.calculate_bollinger_bands(sample_data['close'])
        
        assert 'upper' in bb and 'middle' in bb and 'lower' in bb
        valid = ~bb['upper'].isna()
        assert (bb['upper'][valid] >= bb['middle'][valid]).all()
        assert (bb['middle'][valid] >= bb['lower'][valid]).all()
    
    def test_macd(self, sample_data):
        """Test MACD calculation"""
        macd = indicators.calculate_macd(sample_data['close'])
        
        assert 'macd' in macd and 'signal' in macd and 'histogram' in macd
        assert len(macd['macd']) == len(sample_data)
    
    def test_ema(self, sample_data):
        """Test EMA calculation"""
        ema = indicators.calculate_ema(sample_data['close'], period=50)
        
        assert not ema.isna().all(), "EMA should have values"
        assert len(ema) == len(sample_data)


class TestPatterns:
    """Test pattern detection module"""
    
    def test_fvg_detection(self, sample_data):
        """Test Fair Value Gap detection"""
        fvgs = patterns.detect_fair_value_gaps(
            sample_data['high'],
            sample_data['low'],
            sample_data['close']
        )
        
        assert isinstance(fvgs, list), "Should return list of FVGs"
        # FVGs are rare, may be empty
    
    def test_consolidation_detection(self, sample_data):
        """Test consolidation pattern detection"""
        consol = patterns.detect_consolidation(
            sample_data['high'],
            sample_data['low'],
            sample_data['close']
        )
        
        assert isinstance(consol, pd.Series), "Should return pandas Series"
        assert len(consol) == len(sample_data)
    
    def test_engulfing_patterns(self, sample_data):
        """Test engulfing pattern detection"""
        engulfing = patterns.detect_engulfing_patterns(
            sample_data['open'],
            sample_data['high'],
            sample_data['low'],
            sample_data['close']
        )
        
        assert 'bullish' in engulfing and 'bearish' in engulfing
        assert isinstance(engulfing['bullish'], pd.Series)


class TestRegimeFeatures:
    """Test regime detection module"""
    
    def test_trend_regime_detection(self, sample_data):
        """Test trend regime detection"""
        regime = regime_features.detect_trend_regime(sample_data['close'])
        
        assert isinstance(regime, pd.Series)
        assert len(regime) == len(sample_data)
        valid_regimes = ['BULLISH', 'BEARISH', 'SIDEWAYS', 'UNDEFINED']
        assert regime.isin(valid_regimes).all()
    
    def test_volatility_regime_detection(self, sample_data):
        """Test volatility regime detection"""
        regime = regime_features.detect_volatility_regime(
            sample_data['high'],
            sample_data['low'],
            sample_data['close']
        )
        
        assert isinstance(regime, pd.Series)
        valid_vol_regimes = ['LOW', 'NORMAL', 'HIGH', 'EXTREME']
        assert regime.isin(valid_vol_regimes).all()


class TestStrategies:
    """Test individual strategy modules"""
    
    def test_trap_reversal_strategy(self, sample_data):
        """Test Trap Reversal Scalper"""
        strategy = TrapReversalScalper(pin=841921)
        
        assert strategy.pin_verified
        assert strategy.name == "TrapReversalScalper"
        
        # Generate signals (may be empty with random data)
        signals = strategy.generate_signals(sample_data)
        assert isinstance(signals, list)
    
    def test_ema_scalper_strategy(self, sample_data):
        """Test EMA Scalper"""
        strategy = EMAScalper(pin=841921)
        
        assert strategy.pin_verified
        assert strategy.name == "EMAScalper"
        assert strategy.tp_pct / strategy.sl_pct == 2.0, "Should have 2:1 R:R"
        
        # Generate signals
        signals = strategy.generate_signals(sample_data)
        assert isinstance(signals, list)
    
    def test_price_action_strategy(self, sample_data):
        """Test Price Action Holy Grail"""
        strategy = PriceActionHolyGrail(pin=841921)
        
        assert strategy.pin_verified
        assert strategy.name == "PriceActionHolyGrail"
        
        # Generate signals
        signals = strategy.generate_signals(sample_data)
        assert isinstance(signals, list)
    
    def test_fib_confluence_strategy(self, sample_data):
        """Test Fibonacci Confluence"""
        strategy = FibConfluence(pin=841921)
        
        assert strategy.pin_verified
        assert strategy.name == "FibConfluence"
        assert strategy.fib_50 == 0.50
        assert strategy.fib_618 == 0.618
        
        # Generate signals
        signals = strategy.generate_signals(sample_data)
        assert isinstance(signals, list)
    
    def test_invalid_pin(self):
        """Test PIN authentication"""
        with pytest.raises(ValueError):
            TrapReversalScalper(pin=999999)


class TestPackManager:
    """Test strategy pack manager"""
    
    def test_pack_manager_initialization(self):
        """Test pack manager creation"""
        manager = StrategyPackManager(pin=841921)
        
        assert manager.pin_verified
        assert manager.name == "StrategyPackManager"
        assert manager.min_confidence == 0.60
        assert manager.min_strategies == 2
    
    def test_strategy_registration(self):
        """Test strategy registration"""
        manager = StrategyPackManager(pin=841921)
        strategy = TrapReversalScalper(pin=841921)
        
        manager.register_strategy(strategy, weight=1.0)
        
        assert "TrapReversalScalper" in manager.strategies
        assert manager.strategy_weights["TrapReversalScalper"] == 1.0
    
    def test_default_pack_manager(self):
        """Test default pack manager with all strategies"""
        manager = create_default_pack_manager()
        
        assert len(manager.strategies) == 4
        assert "TrapReversalScalper" in manager.strategies
        assert "EMAScalper" in manager.strategies
        assert "PriceActionHolyGrail" in manager.strategies
        assert "FibConfluence" in manager.strategies
    
    def test_consensus_signal_generation(self, sample_data):
        """Test consensus signal generation"""
        manager = create_default_pack_manager()
        
        # Generate consensus signals
        signals = manager.generate_consensus_signals(sample_data)
        
        assert isinstance(signals, list)
        # Signals may be empty with random data, but should not error


def test_module_imports():
    """Test that all modules can be imported"""
    import research_strategies
    from research_strategies import indicators
    from research_strategies import patterns
    from research_strategies import regime_features
    from research_strategies import pack_manager
    from research_strategies.trap_reversal_scalper import TrapReversalScalper
    from research_strategies.ema_scalper import EMAScalper
    from research_strategies.price_action_holy_grail import PriceActionHolyGrail
    from research_strategies.fib_confluence import FibConfluence
    
    assert research_strategies.__pin__ == 841921


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
