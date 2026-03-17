#!/usr/bin/env python3
"""
Mode Manager - .upgrade_toggle Integration
Reads system mode from .upgrade_toggle file and maps to connector environments
Supports PAPER mode for paper/practice trading with real API endpoints
"""

from pathlib import Path
from typing import Dict
import sys

# Simple logger replacement (avoid util/logging.py conflict)
class SimpleLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

logger = SimpleLogger()

# Project paths - Use script's parent directory or fallback to hardcoded path
try:
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
except NameError:
    # Fallback for interactive mode
    PROJECT_ROOT = Path("/home/ing/RICK/RICK_LIVE_CLEAN")

TOGGLE_FILE = PROJECT_ROOT / ".upgrade_toggle"

MODE_MAP = {
    "PAPER": {"oanda": "practice", "coinbase": "sandbox", "description": "PAPER mode - Paper/practice trading with real API endpoints", "api": True},
}


def read_upgrade_toggle() -> str:
    """
    Read current mode from .upgrade_toggle file

    Returns:
        str: Current mode ('PAPER')
    """
    try:
        if not TOGGLE_FILE.exists():
            logger.warning(f".upgrade_toggle file not found at {TOGGLE_FILE}, defaulting to PAPER")
            # Create with PAPER default
            write_upgrade_toggle("PAPER")
            return "PAPER"

        with open(TOGGLE_FILE, 'r') as f:
            mode = f.read().strip().upper()

        # Validate mode
        if mode not in MODE_MAP:
            logger.warning(f"Invalid mode '{mode}' in .upgrade_toggle, defaulting to PAPER")
            return "PAPER"

        return mode

    except Exception as e:
        logger.error(f"Failed to read .upgrade_toggle: {e}, defaulting to PAPER")
        return "PAPER"


def write_upgrade_toggle(mode: str) -> bool:
    """
    Write mode to .upgrade_toggle file

    Args:
        mode: Mode to set ('PAPER')

    Returns:
        bool: Success
    """
    try:
        mode = mode.strip().upper()
        
        if mode not in MODE_MAP:
            logger.error(f"Invalid mode '{mode}', must be one of: {list(MODE_MAP.keys())}")
            return False
        
        with open(TOGGLE_FILE, 'w') as f:
            f.write(mode + '\n')
        
        logger.info(f"✅ Updated .upgrade_toggle to: {mode}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to write .upgrade_toggle: {e}")
        return False


def get_connector_environment(venue: str) -> str:
    """
    Get connector environment based on current .upgrade_toggle mode
    
    Args:
        venue: 'oanda' or 'coinbase'
    
    Returns:
        str: Environment ('practice', 'sandbox', or 'live')
    """
    mode = read_upgrade_toggle()
    
    if venue.lower() not in MODE_MAP[mode]:
        logger.warning(f"Unknown venue '{venue}', defaulting to practice/sandbox")
        return "practice" if venue.lower() == "oanda" else "sandbox"
    
    environment = MODE_MAP[mode][venue.lower()]
    
    logger.info(f"Mode: {mode} → {venue.upper()} environment: {environment}")
    
    return environment


def get_mode_info() -> Dict[str, any]:
    """
    Get complete mode information
    
    Returns:
        dict: Mode info with current mode, environments, description, and api flag
    """
    mode = read_upgrade_toggle()
    mode_config = MODE_MAP[mode]
    
    return {
        "mode": mode,
        "oanda_environment": mode_config["oanda"],
        "coinbase_environment": mode_config["coinbase"],
        "description": mode_config["description"],
        "is_paper": mode == "PAPER",
        "api": mode_config["api"],  # True for PAPER
        "toggle_file": str(TOGGLE_FILE)
    }


def switch_mode(new_mode: str) -> bool:
    """
    Switch system mode

    Args:
        new_mode: Target mode ('PAPER')

    Returns:
        bool: Success
    """
    new_mode = new_mode.strip().upper()

    # Validate mode
    if new_mode not in MODE_MAP:
        logger.error(f"Invalid mode '{new_mode}', must be one of: {list(MODE_MAP.keys())}")
        return False

    # Write new mode
    if write_upgrade_toggle(new_mode):
        mode_info = get_mode_info()
        logger.info(f"🔄 Mode switched: {mode_info['description']}")
        logger.info(f"   OANDA → {mode_info['oanda_environment']}")
        logger.info(f"   Coinbase → {mode_info['coinbase_environment']}")
        return True

    return False


if __name__ == "__main__":
    # Test mode manager
    print("🧪 Mode Manager Test\n")

    info = get_mode_info()
    print(f"Current Mode: {info['mode']}")
    print(f"Description: {info['description']}")
    print(f"OANDA: {info['oanda_environment']}")
    print(f"Coinbase: {info['coinbase_environment']}")
    print(f"Is Paper: {info['is_paper']}")
    print(f"API Enabled: {info['api']}")
    print(f"Toggle File: {info['toggle_file']}")
