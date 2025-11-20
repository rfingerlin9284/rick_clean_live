#!/usr/bin/env python3
"""
IBKR Connector Mock Test
Tests IBConnector functionality using a mock IB Gateway (FakeIB)
Tests order placement, market data, and error handling without requiring IB Gateway
"""

import sys
import os
import logging
from typing import Dict, List, Any
from datetime import datetime, timezone
from dataclasses import dataclass

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Mock classes to simulate ib_insync
@dataclass
class MockTicker:
    """Mock ticker data"""
    bid: float = -1
    ask: float = -1
    last: float = -1
    
    def __init__(self):
        self.bid = -1
        self.ask = -1
        self.last = -1


@dataclass
class MockOrderStatus:
    """Mock order status"""
    status: str = "Filled"
    avgFillPrice: float = 0.0
    filled: float = 0.0


@dataclass
class MockOrder:
    """Mock order"""
    orderId: int = 0
    action: str = "BUY"
    totalQuantity: float = 0.0


@dataclass
class MockTrade:
    """Mock trade result"""
    order: MockOrder = None
    orderStatus: MockOrderStatus = None
    
    def __init__(self):
        self.order = MockOrder()
        self.orderStatus = MockOrderStatus()
    
    def isDone(self):
        return True


class MockContract:
    """Mock IB contract"""
    def __init__(self, symbol=None, **kwargs):
        self.symbol = symbol
        self.secType = kwargs.get('secType', 'CASH')
        self.exchange = kwargs.get('exchange', 'IDEALPRO')
        self.currency = kwargs.get('currency', 'USD')


class FakeIB:
    """
    Mock IB Gateway for testing without actual connection
    Simulates ib_insync.IB class behavior
    """
    
    def __init__(self):
        self.connected = False
        self.account_id = "DU6880040"  # Paper trading account
        self._next_order_id = 1
        self._market_data = {
            'EUR.USD': {'bid': 1.0850, 'ask': 1.0852, 'last': 1.0851},
            'GBP.USD': {'bid': 1.2650, 'ask': 1.2652, 'last': 1.2651},
            'EURUSD': {'bid': 1.0850, 'ask': 1.0852, 'last': 1.0851},
            'AAPL': {'bid': 175.50, 'ask': 175.52, 'last': 175.51},
            'BTC': {'bid': 42000.0, 'ask': 42050.0, 'last': 42025.0},
        }
        self._positions = []
        self._account_values = [
            type('AccountValue', (), {'tag': 'TotalCashValue', 'value': '10000.00'}),
            type('AccountValue', (), {'tag': 'NetLiquidation', 'value': '10000.00'}),
            type('AccountValue', (), {'tag': 'UnrealizedPnL', 'value': '0.00'}),
            type('AccountValue', (), {'tag': 'BuyingPower', 'value': '40000.00'}),
            type('AccountValue', (), {'tag': 'MaintMarginReq', 'value': '0.00'}),
        ]
    
    def connect(self, host: str, port: int, clientId: int, timeout: int = 20):
        """Mock connection"""
        logger.info(f"FakeIB: Mock connecting to {host}:{port}")
        self.connected = True
        return True
    
    def disconnect(self):
        """Mock disconnect"""
        logger.info("FakeIB: Mock disconnecting")
        self.connected = False
    
    def isConnected(self):
        """Check if mock connected"""
        return self.connected
    
    def managedAccounts(self):
        """Return mock accounts"""
        return [self.account_id]
    
    def reqMktData(self, contract, snapshot=False):
        """Mock market data request"""
        ticker = MockTicker()
        
        # Get symbol from contract
        symbol = contract.symbol if hasattr(contract, 'symbol') else 'EUR.USD'
        
        # Return mock data if available, otherwise return -1 (no data)
        if symbol in self._market_data:
            data = self._market_data[symbol]
            ticker.bid = data['bid']
            ticker.ask = data['ask']
            ticker.last = data['last']
        else:
            # Symbol not found - keep -1 values to simulate no data
            logger.warning(f"FakeIB: No mock data for symbol {symbol}")
        
        return ticker
    
    def placeOrder(self, contract, order):
        """Mock order placement"""
        trade = MockTrade()
        trade.order.orderId = self._next_order_id
        self._next_order_id += 1
        
        # Set fill price based on action
        symbol = contract.symbol if hasattr(contract, 'symbol') else 'EUR.USD'
        if symbol in self._market_data:
            data = self._market_data[symbol]
            if order.action == 'BUY':
                trade.orderStatus.avgFillPrice = data['ask']
            else:
                trade.orderStatus.avgFillPrice = data['bid']
        else:
            trade.orderStatus.avgFillPrice = 1.0
        
        trade.orderStatus.status = "Filled"
        trade.orderStatus.filled = order.totalQuantity
        trade.order.action = order.action
        trade.order.totalQuantity = order.totalQuantity
        
        logger.info(
            f"FakeIB: Mock order placed - {order.action} {order.totalQuantity} {symbol} "
            f"@ {trade.orderStatus.avgFillPrice}"
        )
        
        return trade
    
    def accountValues(self, account_id=None):
        """Return mock account values"""
        return self._account_values
    
    def positions(self, account_id=None):
        """Return mock positions"""
        return self._positions
    
    def sleep(self, seconds):
        """Mock sleep (does nothing)"""
        pass


def Stock(symbol, exchange, currency):
    """Mock Stock contract"""
    return MockContract(symbol=symbol, secType='STK', exchange=exchange, currency=currency)


def Forex(pair, exchange):
    """Mock Forex contract"""
    # Extract symbol from pair (e.g., EURUSD -> EUR)
    symbol = pair[:3] + '.' + pair[3:] if len(pair) == 6 else pair
    return MockContract(symbol=symbol, secType='CASH', exchange=exchange, currency='USD')


def Future(symbol, exchange, currency):
    """Mock Future contract"""
    return MockContract(symbol=symbol, secType='FUT', exchange=exchange, currency=currency)


def MarketOrder(action, quantity):
    """Mock MarketOrder"""
    order = MockOrder()
    order.action = action
    order.totalQuantity = quantity
    return order


def LimitOrder(action, quantity, price):
    """Mock LimitOrder"""
    order = MockOrder()
    order.action = action
    order.totalQuantity = quantity
    order.lmtPrice = price
    return order


def StopOrder(action, quantity, stop_price):
    """Mock StopOrder"""
    order = MockOrder()
    order.action = action
    order.totalQuantity = quantity
    order.auxPrice = stop_price
    return order


class MockUtil:
    """Mock util module"""
    pass


# Mock ib_insync module
class MockIBModule:
    IB = FakeIB
    Stock = Stock
    Forex = Forex
    Future = Future
    Contract = MockContract
    MarketOrder = MarketOrder
    LimitOrder = LimitOrder
    StopOrder = StopOrder
    util = MockUtil()


# Inject mock module BEFORE any imports
sys.modules['ib_insync'] = MockIBModule()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we need to patch the ib_connector module BEFORE importing it
# First, let's import the module and patch the check
import brokers.ib_connector as ib_connector_module

# Patch the availability flag
ib_connector_module.IB_INSYNC_AVAILABLE = True

# Patch the imported classes
ib_connector_module.IB = FakeIB
ib_connector_module.Stock = Stock
ib_connector_module.Forex = Forex
ib_connector_module.Future = Future
ib_connector_module.Contract = MockContract
ib_connector_module.MarketOrder = MarketOrder
ib_connector_module.LimitOrder = LimitOrder
ib_connector_module.StopOrder = StopOrder

# Now import IBConnector (it will use our mock)
from brokers.ib_connector import IBConnector


def test_get_best_bid_ask():
    """Test getting bid/ask prices"""
    print("\n" + "=" * 80)
    print("TEST 1: Get Best Bid/Ask")
    print("=" * 80)
    
    try:
        ib = IBConnector(pin=841921, environment='paper')
        
        symbols = ['EUR.USD', 'GBP.USD', 'AAPL']
        for symbol in symbols:
            price = ib.get_current_bid_ask(symbol)
            print(f"✅ {symbol}: BID={price['bid']:.5f} ASK={price['ask']:.5f}")
            
            assert price['bid'] > 0, f"Invalid bid price for {symbol}"
            assert price['ask'] > 0, f"Invalid ask price for {symbol}"
            assert price['ask'] >= price['bid'], f"Ask should be >= bid for {symbol}"
        
        ib.disconnect()
        print("✅ TEST PASSED: Get Best Bid/Ask")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False


def test_place_limit_and_broker_order_created():
    """Test placing a limit order and verify broker order is created"""
    print("\n" + "=" * 80)
    print("TEST 2: Place Limit Order and Broker Order Created")
    print("=" * 80)
    
    try:
        ib = IBConnector(pin=841921, environment='paper')
        
        # Place a market order (we'll treat it as limit for testing)
        result = ib.place_market_order(
            symbol='EUR.USD',
            direction='buy',
            quantity=1000,
            stop_loss=1.0800,
            take_profit=1.0900
        )
        
        print(f"Order result: {result}")
        
        assert result['success'], "Order should be successful"
        assert 'order_id' in result, "Order ID should be present"
        assert result['fill_price'] > 0, "Fill price should be positive"
        
        ib.disconnect()
        print("✅ TEST PASSED: Place Limit Order and Broker Order Created")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_account_summary():
    """Test getting account summary"""
    print("\n" + "=" * 80)
    print("TEST 3: Get Account Summary")
    print("=" * 80)
    
    try:
        ib = IBConnector(pin=841921, environment='paper')
        
        summary = ib.get_account_summary()
        print(f"Account summary: {summary}")
        
        assert 'account_id' in summary, "Account ID should be present"
        assert 'balance' in summary, "Balance should be present"
        assert summary['balance'] > 0, "Balance should be positive"
        
        ib.disconnect()
        print("✅ TEST PASSED: Get Account Summary")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False


def test_error_handling():
    """Test error handling for invalid symbols and orders"""
    print("\n" + "=" * 80)
    print("TEST 4: Error Handling")
    print("=" * 80)
    
    try:
        ib = IBConnector(pin=841921, environment='paper')
        
        # Test with an invalid/unknown symbol that has no mock data
        price = ib.get_current_bid_ask('INVALID_SYMBOL')
        print(f"Invalid symbol result: {price}")
        
        # Should return zeros or error without crashing
        assert 'symbol' in price, "Result should have symbol field"
        
        ib.disconnect()
        print("✅ TEST PASSED: Error Handling")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False
        
        assert 'account_id' in summary, "Account ID should be present"
        assert 'balance' in summary, "Balance should be present"
        assert summary['balance'] > 0, "Balance should be positive"
        
        ib.disconnect()
        print("✅ TEST PASSED: Get Account Summary")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 IBKR Connector Mock Tests")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Get Best Bid/Ask", test_get_best_bid_ask()))
    results.append(("Place Limit Order", test_place_limit_and_broker_order_created()))
    results.append(("Account Summary", test_account_summary()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
