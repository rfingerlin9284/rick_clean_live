#!/usr/bin/env python3
"""
Engine Status Checker
Checks the health and status of the trading engine
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
NARRATION_FILE = PROJECT_ROOT / "narration.jsonl"


def check_engine_status():
    """Check if the trading engine is running and healthy"""
    print("=" * 60)
    print("Trading Engine Status Check")
    print("=" * 60)
    print()
    
    # Check if narration file exists
    if not NARRATION_FILE.exists():
        print("⚠️  WARNING: narration.jsonl not found")
        print("   Engine may not have started yet")
        return False
    
    print(f"✅ Narration file found: {NARRATION_FILE}")
    
    # Read last few events
    try:
        with open(NARRATION_FILE, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            print("⚠️  WARNING: No events in narration file")
            return False
        
        print(f"✅ Total events in narration: {len(lines)}")
        
        # Check recent activity (last 5 minutes)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=5)
        
        recent_events = []
        for line in lines[-100:]:  # Check last 100 events
            try:
                event = json.loads(line.strip())
                event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                if event_time > cutoff:
                    recent_events.append(event)
            except:
                continue
        
        print(f"✅ Recent events (last 5 min): {len(recent_events)}")
        
        # Show event types
        event_types = {}
        for event in recent_events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        if event_types:
            print("\n📊 Recent event breakdown:")
            for event_type, count in event_types.items():
                print(f"   {event_type}: {count}")
        
        # Check for errors
        errors = [e for e in recent_events if 'ERROR' in e.get('event_type', '')]
        if errors:
            print(f"\n⚠️  WARNING: {len(errors)} recent errors detected")
            for error in errors[-3:]:  # Show last 3 errors
                print(f"   - {error.get('event_type')}: {error.get('details', {})}")
        else:
            print("\n✅ No recent errors")
        
        # Engine status summary
        print("\n" + "=" * 60)
        if recent_events:
            print("✅ ENGINE STATUS: HEALTHY - Recent activity detected")
        else:
            print("⚠️  ENGINE STATUS: IDLE - No recent activity")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to check engine status: {e}")
        return False


if __name__ == "__main__":
    success = check_engine_status()
    sys.exit(0 if success else 1)
