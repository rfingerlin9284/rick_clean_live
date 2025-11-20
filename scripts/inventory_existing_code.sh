#!/bin/bash
# RICK Frankenstein Assembly - Find and Combine Existing Code
# NO TA-LIB VERSION

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  RICK Frankenstein Assembly - Locate Existing Code            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_FILE="$REPO_ROOT/code_inventory.txt"

echo -e "${BLUE}Searching for RICK components...${NC}"
echo ""

# Create inventory file
echo "RICK Code Inventory - $(date)" > "$INVENTORY_FILE"
echo "============================================" >> "$INVENTORY_FILE"
echo "" >> "$INVENTORY_FILE"

# Search for Charter files
echo -e "${YELLOW}Looking for Charter files...${NC}"
echo "=== CHARTER FILES ===" >> "$INVENTORY_FILE"
find ~ -name "*charter*.py" -type f 2>/dev/null | while read file; do
    if grep -q "PIN.*841921\|class.*Charter" "$file" 2>/dev/null; then
        size=$(wc -l "$file" 2>/dev/null | awk '{print $1}')
        mod=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
        echo "  ✓ $file (${size} lines, ${mod})"
        echo "$file | $size lines | $mod" >> "$INVENTORY_FILE"
    fi
done

# Search for Guardian Gates
echo ""
echo -e "${YELLOW}Looking for Guardian Gates files...${NC}"
echo "" >> "$INVENTORY_FILE"
echo "=== GUARDIAN GATES ===" >> "$INVENTORY_FILE"
find ~ -name "*guardian*.py" -o -name "*gate*.py" -type f 2>/dev/null | while read file; do
    if grep -q "validate_trade\|GuardianGate" "$file" 2>/dev/null; then
        size=$(wc -l "$file" 2>/dev/null | awk '{print $1}')
        mod=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
        echo "  ✓ $file (${size} lines, ${mod})"
        echo "$file | $size lines | $mod" >> "$INVENTORY_FILE"
    fi
done

# Search for Regime Detector
echo ""
echo -e "${YELLOW}Looking for Regime Detector files...${NC}"
echo "" >> "$INVENTORY_FILE"
echo "=== REGIME DETECTOR ===" >> "$INVENTORY_FILE"
find ~ -name "*regime*.py" -type f 2>/dev/null | while read file; do
    if grep -q "BULLISH\|BEARISH\|SIDEWAYS\|detect.*regime" "$file" 2>/dev/null; then
        size=$(wc -l "$file" 2>/dev/null | awk '{print $1}')
        mod=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
        echo "  ✓ $file (${size} lines, ${mod})"
        echo "$file | $size lines | $mod" >> "$INVENTORY_FILE"
    fi
done

# Search for Wolf Pack strategies
echo ""
echo -e "${YELLOW}Looking for Wolf Pack strategies...${NC}"
echo "" >> "$INVENTORY_FILE"
echo "=== WOLF PACK STRATEGIES ===" >> "$INVENTORY_FILE"
find ~ -name "*wolf*.py" -o -name "*bullish*.py" -o -name "*bearish*.py" -o -name "*sideways*.py" -type f 2>/dev/null | while read file; do
    if grep -q "class.*Wolf\|WolfPack" "$file" 2>/dev/null; then
        size=$(wc -l "$file" 2>/dev/null | awk '{print $1}')
        mod=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
        echo "  ✓ $file (${size} lines, ${mod})"
        echo "$file | $size lines | $mod" >> "$INVENTORY_FILE"
    fi
done

# Search for Trading Engines
echo ""
echo -e "${YELLOW}Looking for Trading Engines...${NC}"
echo "" >> "$INVENTORY_FILE"
echo "=== TRADING ENGINES ===" >> "$INVENTORY_FILE"
find ~ -name "*ghost*.py" -o -name "*canary*.py" -o -name "*engine*.py" -type f 2>/dev/null | while read file; do
    if grep -q "class.*Engine\|TradingEngine\|ghost\|canary" "$file" 2>/dev/null; then
        size=$(wc -l "$file" 2>/dev/null | awk '{print $1}')
        mod=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
        echo "  ✓ $file (${size} lines, ${mod})"
        echo "$file | $size lines | $mod" >> "$INVENTORY_FILE"
    fi
done

# Check for TA-Lib usage
echo ""
echo -e "${YELLOW}Checking for TA-Lib usage...${NC}"
echo "" >> "$INVENTORY_FILE"
echo "=== FILES WITH TA-LIB (NEED REPLACEMENT) ===" >> "$INVENTORY_FILE"
grep -r "import talib" ~ --include="*.py" -l 2>/dev/null | head -20 | while read file; do
    echo "  ⚠ $file - Contains TA-Lib import"
    echo "$file - NEEDS TA-LIB REMOVAL" >> "$INVENTORY_FILE"
done

# Summary
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Inventory Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Results saved to:${NC} $INVENTORY_FILE"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review inventory: ${BLUE}cat $INVENTORY_FILE${NC}"
echo "  2. Read Frankenstein guide: ${BLUE}cat VSCODE_AGENT_FRANKENSTEIN_ASSEMBLY.md${NC}"
echo "  3. Give VSCode agent the complete prompt from the guide"
echo "  4. Agent will combine files (removing TA-Lib)"
echo "  5. Verify: ${BLUE}bash scripts/verify_and_activate_all_systems.sh${NC}"
echo ""
echo -e "${GREEN}Ready to Frankenstein! 🧟${NC}"
