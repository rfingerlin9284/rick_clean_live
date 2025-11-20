#!/usr/bin/env python3
"""
Why No Trade Diagnostic Tool
Analyzes why trading signals are not resulting in actual trades.
Checks charter violations, registry blocks, and other gating conditions.
PIN: 841921 | Generated: 2025-11-20
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

try:
    from foundation.rick_charter import RickCharter
    from util.positions_registry import PositionsRegistry
    from util.usd_converter import get_usd_notional
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    RickCharter = None
    PositionsRegistry = None
    get_usd_notional = None


class TradeBlockDiagnostic:
    """Diagnose why trades are being blocked"""
    
    def __init__(self, dev_mode: bool = False):
        """
        Initialize diagnostic tool.
        
        Args:
            dev_mode: Enable development mode (from RICK_DEV_MODE env var)
        """
        self.dev_mode = dev_mode or os.getenv('RICK_DEV_MODE') == '1'
        self.registry = PositionsRegistry() if PositionsRegistry else None
        self.narration_file = Path(__file__).parent.parent / 'narration.jsonl'
        
    def check_charter_compliance(self, symbol: str, position_size: float, 
                                entry_price: float, stop_loss_pips: float,
                                take_profit_pips: float) -> Dict:
        """
        Check if proposed trade meets charter requirements.
        
        Args:
            symbol: Trading symbol
            position_size: Position size in units
            entry_price: Entry price
            stop_loss_pips: Stop loss in pips
            take_profit_pips: Take profit in pips
            
        Returns:
            Dictionary with compliance status and any violations
        """
        if not RickCharter:
            return {'compliant': False, 'error': 'Charter module not available'}
        
        violations = []
        
        # Calculate notional value
        notional_usd = position_size * entry_price
        if get_usd_notional:
            try:
                notional_usd = get_usd_notional(symbol, position_size, entry_price)
            except Exception:
                pass
        
        # Check minimum notional
        if notional_usd < RickCharter.MIN_NOTIONAL_USD:
            violations.append({
                'type': 'MIN_NOTIONAL_VIOLATION',
                'notional_usd': notional_usd,
                'min_required_usd': RickCharter.MIN_NOTIONAL_USD,
                'message': f'Notional ${notional_usd:,.2f} < ${RickCharter.MIN_NOTIONAL_USD:,}'
            })
        
        # Check risk-reward ratio
        if take_profit_pips > 0 and stop_loss_pips > 0:
            rr_ratio = take_profit_pips / stop_loss_pips
            if rr_ratio < RickCharter.MIN_RISK_REWARD_RATIO:
                violations.append({
                    'type': 'MIN_RR_VIOLATION',
                    'rr_ratio': rr_ratio,
                    'min_required': RickCharter.MIN_RISK_REWARD_RATIO,
                    'message': f'R:R {rr_ratio:.2f} < {RickCharter.MIN_RISK_REWARD_RATIO}'
                })
        
        # Check expected PnL at take profit
        pip_value = position_size * (0.0001 if 'JPY' not in symbol else 0.01)
        expected_pnl_usd = take_profit_pips * pip_value
        
        if expected_pnl_usd < RickCharter.MIN_EXPECTED_PNL_USD:
            violations.append({
                'type': 'MIN_EXPECTED_PNL_VIOLATION',
                'expected_pnl_usd': expected_pnl_usd,
                'min_required_usd': RickCharter.MIN_EXPECTED_PNL_USD,
                'message': f'Expected PnL ${expected_pnl_usd:.2f} < ${RickCharter.MIN_EXPECTED_PNL_USD}'
            })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'notional_usd': notional_usd,
            'rr_ratio': take_profit_pips / stop_loss_pips if stop_loss_pips > 0 else 0,
            'expected_pnl_usd': expected_pnl_usd
        }
    
    def check_registry_block(self, symbol: str) -> Dict:
        """
        Check if symbol is blocked by positions registry.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with registry status
        """
        if not self.registry:
            return {'blocked': False, 'error': 'Registry not available'}
        
        try:
            available = self.registry.is_symbol_available(symbol)
            
            if not available:
                positions = self.registry.get_active_positions()
                if symbol in positions:
                    return {
                        'blocked': True,
                        'reason': 'SYMBOL_ALREADY_IN_USE',
                        'details': positions[symbol]
                    }
            
            return {'blocked': False, 'available': True}
            
        except Exception as e:
            return {'blocked': False, 'error': str(e)}
    
    def analyze_recent_violations(self, symbol: Optional[str] = None, 
                                 limit: int = 10) -> List[Dict]:
        """
        Analyze recent charter violations from narration log.
        
        Args:
            symbol: Optional symbol filter
            limit: Maximum number of violations to return
            
        Returns:
            List of recent violations
        """
        if not self.narration_file.exists():
            return []
        
        violations = []
        
        try:
            with open(self.narration_file, 'r') as f:
                # Read last N lines efficiently
                lines = []
                for line in f:
                    lines.append(line)
                    if len(lines) > 1000:  # Keep last 1000 lines in memory
                        lines.pop(0)
                
                # Parse violations
                for line in reversed(lines):
                    try:
                        event = json.loads(line.strip())
                        if event.get('event_type') == 'CHARTER_VIOLATION':
                            if symbol is None or event.get('symbol') == symbol:
                                violations.append(event)
                                if len(violations) >= limit:
                                    break
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            print(f"Error reading narration file: {e}")
        
        return violations
    
    def diagnose_symbol(self, symbol: str) -> Dict:
        """
        Complete diagnostic for why a symbol might not be trading.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Comprehensive diagnostic report
        """
        report = {
            'symbol': symbol,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'dev_mode': self.dev_mode,
            'checks': {}
        }
        
        # Check registry
        registry_status = self.check_registry_block(symbol)
        report['checks']['registry'] = registry_status
        
        # Check recent violations
        recent_violations = self.analyze_recent_violations(symbol, limit=5)
        report['checks']['recent_violations'] = recent_violations
        
        # Example charter check with typical values
        # In real usage, these would come from signal generator
        example_check = self.check_charter_compliance(
            symbol=symbol,
            position_size=15000,  # Example size
            entry_price=1.0800,   # Example price
            stop_loss_pips=25,    # Example SL
            take_profit_pips=80   # Example TP
        )
        report['checks']['charter_example'] = example_check
        
        # Determine primary reason for no trade
        if registry_status.get('blocked'):
            report['primary_reason'] = 'BROKER_REGISTRY_BLOCK'
            report['message'] = f"Symbol {symbol} already in use on {registry_status['details']['platform']}"
        elif recent_violations:
            latest = recent_violations[0]
            violation_type = latest.get('details', {}).get('violation', 'UNKNOWN')
            report['primary_reason'] = violation_type
            report['message'] = f"Recent charter violation: {violation_type}"
        else:
            report['primary_reason'] = 'NO_SIGNAL'
            report['message'] = 'No trading signal currently available'
        
        return report


def main():
    """CLI interface for trade diagnostics"""
    parser = argparse.ArgumentParser(
        description='Diagnose why trades are not being placed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --symbols EUR_USD,GBP_USD,USD_JPY
  %(prog)s --symbol EUR_USD --verbose
  RICK_DEV_MODE=1 %(prog)s --symbols EUR_USD
        """
    )
    
    parser.add_argument('--symbol', type=str, help='Single symbol to diagnose')
    parser.add_argument('--symbols', type=str, help='Comma-separated symbols to diagnose')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Determine symbols to check
    symbols = []
    if args.symbol:
        symbols = [args.symbol]
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(',')]
    else:
        parser.error('Must specify --symbol or --symbols')
    
    # Create diagnostic tool
    diagnostic = TradeBlockDiagnostic()
    
    # Run diagnostics
    results = []
    for symbol in symbols:
        result = diagnostic.diagnose_symbol(symbol)
        results.append(result)
        
        if not args.json:
            print(f"\n{'='*60}")
            print(f"Diagnostic Report: {symbol}")
            print(f"{'='*60}")
            print(f"Primary Reason: {result['primary_reason']}")
            print(f"Message: {result['message']}")
            
            if args.verbose:
                print(f"\nRegistry Status:")
                print(json.dumps(result['checks']['registry'], indent=2))
                
                if result['checks']['recent_violations']:
                    print(f"\nRecent Violations ({len(result['checks']['recent_violations'])}):")
                    for v in result['checks']['recent_violations']:
                        print(f"  - {v['timestamp']}: {v['details'].get('violation', 'UNKNOWN')}")
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}\n")


if __name__ == '__main__':
    main()
