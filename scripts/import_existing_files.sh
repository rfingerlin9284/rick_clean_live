#!/bin/bash
# Quick Import Script for Existing RICK Files
# Use this to copy your existing RICK implementation files into this repository

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      RICK System - Import Existing Files                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Default source paths (modify these to match your local setup)
RICK_LIVE_CLEAN="${1:-/home/ing/RICK/RICK_LIVE_CLEAN}"
R_H_UNI="${2:-/home/ing/RICK/R_H_UNI}"

echo -e "${BLUE}Source Paths:${NC}"
echo "  RICK_LIVE_CLEAN: $RICK_LIVE_CLEAN"
echo "  R_H_UNI: $R_H_UNI"
echo ""

# Check if source directories exist
if [ ! -d "$RICK_LIVE_CLEAN" ]; then
    echo -e "${RED}ERROR: $RICK_LIVE_CLEAN does not exist${NC}"
    echo ""
    echo "Usage: $0 [RICK_LIVE_CLEAN_PATH] [R_H_UNI_PATH]"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/RICK_LIVE_CLEAN /path/to/R_H_UNI"
    exit 1
fi

# Get repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo -e "${BLUE}Target Repository:${NC} $REPO_ROOT"
echo ""

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p foundation hive logic strategies risk brokers

echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Copy Foundation Layer
echo -e "${YELLOW}Copying Foundation Layer...${NC}"
if [ -d "$RICK_LIVE_CLEAN/foundation" ]; then
    cp -r "$RICK_LIVE_CLEAN/foundation/"* ./foundation/ 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Foundation files copied"
else
    echo -e "${YELLOW}⚠${NC} Foundation directory not found in source"
fi

# Copy Hive Layer
echo -e "${YELLOW}Copying Hive Layer...${NC}"
if [ -d "$RICK_LIVE_CLEAN/hive" ]; then
    cp -r "$RICK_LIVE_CLEAN/hive/"* ./hive/ 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Hive files copied"
else
    echo -e "${YELLOW}⚠${NC} Hive directory not found in source"
fi

# Copy Logic Layer
echo -e "${YELLOW}Copying Logic Layer...${NC}"
if [ -d "$RICK_LIVE_CLEAN/logic" ]; then
    cp -r "$RICK_LIVE_CLEAN/logic/"* ./logic/ 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Logic files copied"
else
    echo -e "${YELLOW}⚠${NC} Logic directory not found in source"
fi

# Copy Risk Management
echo -e "${YELLOW}Copying Risk Management...${NC}"
if [ -d "$RICK_LIVE_CLEAN/risk" ]; then
    cp -r "$RICK_LIVE_CLEAN/risk/"* ./risk/ 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Risk files copied"
else
    echo -e "${YELLOW}⚠${NC} Risk directory not found in source"
fi

# Copy Brokers
echo -e "${YELLOW}Copying Broker Integration...${NC}"
if [ -d "$RICK_LIVE_CLEAN/brokers" ]; then
    cp -r "$RICK_LIVE_CLEAN/brokers/"* ./brokers/ 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Broker files copied"
else
    echo -e "${YELLOW}⚠${NC} Brokers directory not found in source"
fi

# Copy Trading Engines
echo -e "${YELLOW}Copying Trading Engines...${NC}"
if [ -f "$RICK_LIVE_CLEAN/ghost_trading_charter_compliant.py" ]; then
    cp "$RICK_LIVE_CLEAN/ghost_trading_charter_compliant.py" ./
    echo -e "${GREEN}✓${NC} ghost_trading_charter_compliant.py copied"
fi

if [ -f "$RICK_LIVE_CLEAN/canary_trading_engine.py" ]; then
    cp "$RICK_LIVE_CLEAN/canary_trading_engine.py" ./
    echo -e "${GREEN}✓${NC} canary_trading_engine.py copied"
fi

if [ -f "$RICK_LIVE_CLEAN/capital_manager.py" ]; then
    cp "$RICK_LIVE_CLEAN/capital_manager.py" ./
    echo -e "${GREEN}✓${NC} capital_manager.py copied"
fi

# Copy Wolf Pack Strategies from R_H_UNI
echo -e "${YELLOW}Copying Wolf Pack Strategies...${NC}"
if [ -d "$R_H_UNI/strategies" ]; then
    if [ -f "$R_H_UNI/strategies/bullish_wolf.py" ]; then
        cp "$R_H_UNI/strategies/bullish_wolf.py" ./strategies/
        echo -e "${GREEN}✓${NC} bullish_wolf.py copied"
    fi
    
    if [ -f "$R_H_UNI/strategies/bearish_wolf.py" ]; then
        cp "$R_H_UNI/strategies/bearish_wolf.py" ./strategies/
        echo -e "${GREEN}✓${NC} bearish_wolf.py copied"
    fi
    
    if [ -f "$R_H_UNI/strategies/sideways_wolf.py" ]; then
        cp "$R_H_UNI/strategies/sideways_wolf.py" ./strategies/
        echo -e "${GREEN}✓${NC} sideways_wolf.py copied"
    fi
else
    echo -e "${YELLOW}⚠${NC} Wolf pack strategies not found at $R_H_UNI/strategies"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Import Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Show what was copied
echo -e "${BLUE}Files imported:${NC}"
find foundation hive logic strategies risk brokers -name "*.py" 2>/dev/null | sort
ls -1 *.py 2>/dev/null | grep -E "(ghost|canary|capital)" || true

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Run verification script:"
echo "     ${BLUE}bash scripts/verify_and_activate_all_systems.sh${NC}"
echo ""
echo "  2. If 100% verified, activate Canary:"
echo "     ${BLUE}python3 canary_trading_engine.py --continuous --duration 45${NC}"
echo ""
echo -e "${GREEN}Ready to activate RICK! 🚀${NC}"
