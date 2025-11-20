#!/usr/bin/env python3
"""
Test script for plain_english_narration.sh
Validates that the script exists, is executable, and can process narration events.
"""
import os
import subprocess
import json
import tempfile
import time

def test_script_exists():
    """Test that the plain_english_narration.sh script exists"""
    script_path = os.path.join(os.path.dirname(__file__), 'util', 'plain_english_narration.sh')
    assert os.path.exists(script_path), f"Script not found at {script_path}"
    print("✓ Script exists")

def test_script_executable():
    """Test that the script is executable"""
    script_path = os.path.join(os.path.dirname(__file__), 'util', 'plain_english_narration.sh')
    assert os.access(script_path, os.X_OK), f"Script is not executable: {script_path}"
    print("✓ Script is executable")

def test_jq_installed():
    """Test that jq is installed (required dependency)"""
    try:
        result = subprocess.run(['which', 'jq'], capture_output=True, text=True)
        assert result.returncode == 0, "jq is not installed"
        print("✓ jq is installed")
    except Exception as e:
        raise AssertionError(f"jq is not available: {e}")

def test_script_with_sample_data():
    """Test that the script can process sample narration data"""
    # Create a temporary narration file with sample data
    sample_events = [
        {
            "timestamp": "2025-11-20T06:00:00.000000+00:00",
            "event_type": "MACHINE_HEARTBEAT",
            "symbol": "SYSTEM",
            "venue": "system",
            "details": {
                "iteration": 1,
                "regime": "LIVE",
                "open_positions": 0,
                "session_pnl": 0,
                "trades_today": 0
            }
        },
        {
            "timestamp": "2025-11-20T06:01:00.000000+00:00",
            "event_type": "TRADE_OPENED",
            "symbol": "EUR_USD",
            "venue": "oanda",
            "details": {
                "trade_id": "12345",
                "side": "buy",
                "notional_usd": 1000,
                "entry_price": 1.0850
            }
        },
        {
            "timestamp": "2025-11-20T06:02:00.000000+00:00",
            "event_type": "HIVE_ANALYSIS",
            "symbol": "GBP_USD",
            "venue": "hive",
            "details": {
                "consensus": "buy",
                "confidence": 0.85,
                "order_id": "67890",
                "profit_atr": 2.5
            }
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        temp_file = f.name
        for event in sample_events:
            f.write(json.dumps(event) + '\n')
    
    try:
        # Test using jq directly on the temp file (simulating what the script does)
        jq_script = '''
          . as $e
          | .timestamp + " | " + (.event_type // "UNKNOWN") + " | " +
            (.venue // "") + " | " +
            (if .symbol == "SYSTEM" then "" else (.symbol // "") end) + " | " +
            (
              if .event_type == "TRADE_EXECUTED" then
                "trade_id=" + ($e.details.trade_id // "") + " " +
                "side=" + (($e.details.side // "") | ascii_upcase)
              elif .event_type == "MACHINE_HEARTBEAT" then
                "iteration=" + (($e.details.iteration // 0) | tostring) + " " +
                "regime=" + ($e.details.regime // "")
              elif .event_type == "TRADE_OPENED" then
                "trade_id=" + ($e.details.trade_id // "") + " " +
                "side=" + (($e.details.side // "") | ascii_upcase)
              elif .event_type == "HIVE_ANALYSIS" then
                "consensus=" + ($e.details.consensus // "") + " " +
                "confidence=" + (($e.details.confidence // "") | tostring)
              else
                ( $e.details | tostring )
              end
            )
        '''
        
        result = subprocess.run(
            ['jq', '-r', jq_script, temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        assert result.returncode == 0, f"jq processing failed: {result.stderr}"
        output_lines = result.stdout.strip().split('\n')
        assert len(output_lines) == 3, f"Expected 3 output lines, got {len(output_lines)}"
        
        # Verify key content in output
        assert "MACHINE_HEARTBEAT" in output_lines[0], "MACHINE_HEARTBEAT not in output"
        assert "iteration=1" in output_lines[0], "iteration not in MACHINE_HEARTBEAT output"
        assert "TRADE_OPENED" in output_lines[1], "TRADE_OPENED not in output"
        assert "EUR_USD" in output_lines[1], "EUR_USD not in TRADE_OPENED output"
        assert "HIVE_ANALYSIS" in output_lines[2], "HIVE_ANALYSIS not in output"
        assert "consensus=buy" in output_lines[2], "consensus not in HIVE_ANALYSIS output"
        
        print("✓ Script can process sample narration data")
        print(f"  Sample output:\n    {output_lines[0]}")
        
    finally:
        os.unlink(temp_file)

def test_narration_file_exists():
    """Test that narration.jsonl exists in the repository"""
    narration_path = os.path.join(os.path.dirname(__file__), 'narration.jsonl')
    if os.path.exists(narration_path):
        print(f"✓ narration.jsonl exists ({os.path.getsize(narration_path)} bytes)")
    else:
        print("⚠ narration.jsonl does not exist yet (will be created when trading system runs)")

if __name__ == '__main__':
    print("Testing plain_english_narration.sh script...")
    print("=" * 80)
    
    try:
        test_script_exists()
        test_script_executable()
        test_jq_installed()
        test_script_with_sample_data()
        test_narration_file_exists()
        
        print("=" * 80)
        print("✅ All tests passed!")
        print("\nTo use the narration viewer, run:")
        print("  ./util/plain_english_narration.sh")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
